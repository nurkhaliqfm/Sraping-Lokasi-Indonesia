import traceback
import logging
import os
from utils.driver import get_chrome_options
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict
from typing import Optional, List, Dict

SCREENSHOT_DIR = Path(os.getenv("SCREENSHOT_DIR", "data/screenshoot"))
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_driver():
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=get_chrome_options(),
    )


def parse_row(html: str, rule: Dict[str, int]) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    columns = soup.find_all("td")
    return {
        key: (columns[index].text.strip() if index < len(columns) else "")
        for key, index in rule.items()
    }


def scraper_region(
    url: str,
    selected_rule: str,
    rule: Dict[str, int],
    timeout: int = 5,
    locations: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, str]]:

    if not rule:
        raise ValueError("⚠️ 'rule' dictionary is empty or invalid.")

    if locations is None:
        locations = []

    driver = None

    try:
        driver = create_driver()
        driver.get(url)

        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//form[@name='pilihnya']"))
        )

        eTableAnchor = driver.find_element(
            By.XPATH,
            "//tbody[@class='header_mentok']",
        )

        eTableBodyProvinsi = eTableAnchor.find_element(By.XPATH, "following-sibling::*")
        eItemsTableProvinsi = eTableBodyProvinsi.find_elements(By.TAG_NAME, "tr")

        for eItemTableProvinsi in eItemsTableProvinsi:
            item_location = parse_row(
                eItemTableProvinsi.get_attribute("innerHTML"), rule
            )
            locations.append(item_location)

        if locations:
            locations.pop()

        return locations

    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        screenshot_path = SCREENSHOT_DIR / f"failed-log-{selected_rule}-{timestamp}.png"

        if driver:
            try:
                driver.save_screenshot(str(screenshot_path))
            except Exception as ss_err:
                logger.warning(f"⚠️ Could not save screenshot: {ss_err}")

        logger.error(f"❌ Scraping failed for rule '{selected_rule}' at {url}: {e}")
        traceback.print_exc()

        return []

    finally:
        if driver:
            driver.quit()
            logger.info(
                f"✅ Successfully scraped {len(locations)} rows for '{selected_rule}'"
            )
