from selenium.webdriver.chrome.options import Options
import os


def get_chrome_options() -> Options:
    options = Options()
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    )
    if os.getenv("HEADLESS", "False").lower() == "true":
        options.add_argument("--headless")
    return options
