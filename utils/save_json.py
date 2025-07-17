import os
import json
import logging

FOLDER_PATH = "data/lokasi"
logging.basicConfig(level=logging.INFO)


def save_json(data, filename):
    os.makedirs(FOLDER_PATH, exist_ok=True)
    path = os.path.join(FOLDER_PATH, f"{filename}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logging.info(f"📁 Saved JSON to: {path}")
