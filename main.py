import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

URL = os.getenv("URL")
CURRENT_TIME = datetime.now().timestamp()


chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")

try:
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options,
    )

    driver.get(URL)

    try:
        isCloudFlareIsPass = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//form[@name='pilihnya']"))
        )

        # driver.save_screenshot(f"data/screenshoot/success-{CURRENT_TIME}.png")

        eTable = driver.find_element(
            By.XPATH,
            "//table[@class='header_mentok']",
        ).get_attribute("innerHTML")

        print(eTable)

    except:
        # driver.save_screenshot(f"data/screenshoot/failed{CURRENT_TIME}.png")
        print("Failed to scrap")


finally:
    print(f"Done Sraping")
