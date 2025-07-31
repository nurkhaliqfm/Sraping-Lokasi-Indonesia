from dotenv import load_dotenv
import os
import json
from pathlib import Path
from scraper import scraper_region
from utils.save_json import save_json
from datetime import datetime

load_dotenv(override=True)

CURRENT_TIMESTAMP = datetime.now().isoformat(timespec="milliseconds")
URL_BASE = os.getenv("URL")
DATA_DIR = Path("data/lokasi")
RULE_LOKASI = {
    "provinsi": {"Nama": 1, "Kode": 11},
    "kabupaten": {"Nama": 2, "Type": 1, "Kode": 8},
    "kecamatan": {"Nama": 1, "Pos": 2, "Type": 6, "Kabupaten": 7, "Kode": 5},
    "desa": {"Nama": 2, "Pos": 1, "Kode": 3},
}


def load_json(file_path: Path):
    if not file_path.exists():
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_provinsi():
    print("🧭 Scraping Provinsi...")
    url = f"{URL_BASE}?_i=provinsi-kodepos&perhal=60&urut=&asc=000011111&sby=000000&daerah=&jobs="
    locations = []
    scraped_data = scraper_region(
        url=url,
        level="provinsi",
        name="provinsi",
        rule=RULE_LOKASI["provinsi"],
        locations=locations,
    )

    ref_provinsi = [
        {
            "id": i + 1,
            "nama": item["Nama"],
            "kode": item["Kode"],
            "createdAt": CURRENT_TIMESTAMP,
            "updatedAt": CURRENT_TIMESTAMP,
        }
        for i, item in enumerate(scraped_data)
    ]

    save_json(ref_provinsi, "ref_provinsi")


def run_kabupaten():
    provinsi_path = DATA_DIR / "ref_provinsi.json"
    provinsi_list = load_json(provinsi_path)

    if not provinsi_list:
        print("❌ Missing provinsi data. Please run Provinsi scraping first.")
        return

    print("📍 Scraping Kabupaten for each Provinsi...")

    scraped_data = []
    for prov in provinsi_list:
        locations = []
        location = prov["nama"]
        url = f"{URL_BASE}?_i=kota-kodepos&sby=000000&daerah=Provinsi&jobs={location}"
        scraper_region(
            url=url,
            level="kecamatan",
            name=f"kabupaten_{location}",
            rule=RULE_LOKASI["kabupaten"],
            locations=locations,
        )

        scraped_data.extend(
            [{**item, "ref_provinsi_id": prov["id"]} for item in locations]
        )

    ref_kabupaten = [
        {
            "id": i + 1,
            "nama": f"{item['Type']} {item['Nama']}",
            "slug": item["Nama"],
            "kode": item["Kode"],
            "type": item["Type"],
            "ref_provinsi_id": item["ref_provinsi_id"],
            "createdAt": CURRENT_TIMESTAMP,
            "updatedAt": CURRENT_TIMESTAMP,
        }
        for i, item in enumerate(scraped_data)
    ]

    save_json(ref_kabupaten, "ref_kabupaten")


def run_kecamatan():
    kabupaten_path = DATA_DIR / "ref_kabupaten.json"
    kabupaten_list = load_json(kabupaten_path)

    if not kabupaten_list:
        print("❌ Missing kabupaten data. Please run Kabupaten scraping first.")
        return

    print("📍 Scraping Kecamatan for each Kabupaten...")

    scraped_data = []
    for kab in kabupaten_list:
        locations = []
        location = kab["slug"]
        type = kab["type"]
        url = (
            f"{URL_BASE}?_i=kecamatan-kodepos&sby=000000&daerah={type}&jobs={location}"
        )
        scraper_region(
            url,
            level="kecamatan",
            name=f"kecamatan_{location}",
            rule=RULE_LOKASI["kecamatan"],
            locations=locations,
        )

        scraped_data.extend(
            [{**item, "ref_kabupaten_kota_id": kab["id"]} for item in locations]
        )

    ref_kecamatan = [
        {
            "id": i + 1,
            "nama": item["Nama"],
            "kode": item["Kode"],
            "ref_kabupaten_kota_id": item["ref_kabupaten_kota_id"],
            "createdAt": CURRENT_TIMESTAMP,
            "updatedAt": CURRENT_TIMESTAMP,
        }
        for i, item in enumerate(scraped_data)
    ]

    save_json(ref_kecamatan, "ref_kecamatan")


def run_desa():
    kabupaten_path = DATA_DIR / "ref_kabupaten.json"
    kabupaten_list = load_json(kabupaten_path)
    ref_kabupaten_kota_id = {kab["id"]: kab for kab in kabupaten_list}

    kecamatan_path = DATA_DIR / "ref_kecamatan.json"
    kecamatan_list = load_json(kecamatan_path)

    if not kecamatan_list:
        print("❌ Missing kecamatan data. Please run Kecamatan scraping first.")
        return

    print("📍 Scraping Desa for each Kecamatan...")

    scraped_data = []
    for kec in kecamatan_list:
        locations = []
        location = kec["nama"]

        kab = ref_kabupaten_kota_id.get(kec["ref_kabupaten_kota_id"])
        if kab is None:
            print(
                f"❌ Missing kabupaten data with id {kec['ref_kabupaten_kota_id']} in kecamatan {kec['nama']}. Please re-run Kecamatan scraping again."
            )
            break

        url = f"{URL_BASE}?_i=desa-kodepos&sby=000000&daerah=Kecamatan-{kab['type']}-{kab['slug']}&jobs={location}"

        scraper_region(
            url,
            level="kecamatan",
            name=f"kecamatan_{location}",
            rule=RULE_LOKASI["kecamatan"],
            locations=locations,
        )

        scraped_data.extend(
            [{**item, "ref_kecamatan_id": kab["id"]} for item in locations]
        )

    ref_desa_kelurahan = [
        {
            "id": i + 1,
            "nama": item["Nama"],
            "kode": item["Kode"],
            "pos": item["Pos"],
            "ref_kecamatan_id": item["ref_kecamatan_id"],
            "createdAt": CURRENT_TIMESTAMP,
            "updatedAt": CURRENT_TIMESTAMP,
        }
        for i, item in enumerate(scraped_data)
    ]

    save_json(ref_desa_kelurahan, "ref_desa_kelurahan")


def main():
    choice_map = {
        "1": ("provinsi", run_provinsi),
        "2": ("kabupaten", run_kabupaten),
        "3": ("kecamatan", run_kecamatan),
        "4": ("kecamatan", run_desa),
    }

    while True:
        print("\n📦 What do you want to scrape?")
        print("1. Provinsi\n2. Kabupaten\n3. Kecamatan\n4. Desa\n0. Exit")
        choice = input("Enter number (0–4): ").strip()

        if choice == "0":
            print("👋 Exiting.")
            break

        selected = choice_map.get(choice)
        if not selected:
            print("❌ Invalid choice.")
            continue

        level, func = selected
        func()


if __name__ == "__main__":
    main()
