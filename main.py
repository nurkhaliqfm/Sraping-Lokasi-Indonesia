from dotenv import load_dotenv
import os
import json
from pathlib import Path
from scraper import scraper_region

load_dotenv(override=True)

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
    scraper_region(url, "provinsi", RULE_LOKASI["provinsi"])


def run_kabupaten():
    provinsi_path = DATA_DIR / "provinsi.json"
    provinsi_list = load_json(provinsi_path)

    if not provinsi_list:
        print("❌ Missing provinsi data. Please run Provinsi scraping first.")
        return

    print("📍 Scraping Kabupaten for each Provinsi...")
    for prov in provinsi_list:
        location = prov["Nama"]
        url = f"{URL_BASE}?_i=kota-kodepos&sby=000000&daerah=Provinsi&jobs={location}"
        scraper_region(url, f"kabupaten_{location}", RULE_LOKASI["kabupaten"])


def run_kecamatan():
    location = "Nama"
    daerah = "Type"

    print("🧭 Scraping Kecamatan...")
    url = f"{URL_BASE}?_i=kecamatan-kodepos&sby=000000&daerah={daerah}&jobs={location}"


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
        # Extend with kecamatan/desa later
    }

    while True:
        print("\n📦 What do you want to scrape?")
        print("1. Provinsi\n2. Kabupaten\n0. Exit")
        choice = input("Enter number (0–2): ").strip()

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
