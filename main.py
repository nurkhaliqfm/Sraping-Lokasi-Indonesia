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
        url, "provinsi", RULE_LOKASI["provinsi"], locations=locations
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
            url, f"kabupaten_{location}", RULE_LOKASI["kabupaten"], locations=locations
        )

        scraped_data.extend(
            [{**item, "ref_provinsi_id": prov["id"]} for item in locations]
        )

    ref_kabupaten = [
        {
            "id": i + 1,
            "nama": f"{item['Type']} {item['Nama']}",
            "kode": item["Kode"],
            "ref_provinsi_id": item["ref_provinsi_id"],
            "createdAt": CURRENT_TIMESTAMP,
            "updatedAt": CURRENT_TIMESTAMP,
        }
        for i, item in enumerate(scraped_data)
    ]

    save_json(ref_kabupaten, "ref_kabupaten")


def run_kecamatan():
    kabupaten_files = Path("data/lokasi").glob("kabupaten_*.json")
    rule = RULE_LOKASI["kecamatan"]

    if not list(kabupaten_files):
        print("❌ Missing kabupaten data. Please run Kabupaten scraping first.")
        return

    print(list(kabupaten_files))

    for kab_file in kabupaten_files:
        try:
            with open(kab_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for item in data:
                location = item.get("Nama")
                daerah = item.get("Kode")

                if not daerah or not location:
                    print(f"⚠️ Skipping invalid item in {kab_file.name}")
                    continue

                url = f"{URL_BASE}?_i=kecamatan-kodepos&sby=000000&daerah={daerah}&jobs={location}"
                print(f"📍 Scraping Kecamatan for Kabupaten: {location} ({daerah})")
                scraper_region(url, f"kecamatan_{location}", rule)

        except Exception as e:
            print(f"❌ Failed to process {kab_file.name}: {e}")


def run_desa():
    location = "Nama"
    daerah = "Type"
    kabupaten = "Kabupaten"

    print("🧭 Scraping Desa...")
    url = f"{URL_BASE}?_i=desa-kodepos&sby=000000&daerah=Kecamatan-{daerah}-{kabupaten}&jobs={location}"


def main():
    choice_map = {
        "1": ("provinsi", run_provinsi),
        "2": ("kabupaten", run_kabupaten),
        "3": ("kecamatan", run_kecamatan),
        # Extend with kecamatan/desa later
    }

    while True:
        print("\n📦 What do you want to scrape?")
        print("1. Provinsi\n2. Kabupaten\n3. Kecamatan\n0. Exit")
        choice = input("Enter number (0–3): ").strip()

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
