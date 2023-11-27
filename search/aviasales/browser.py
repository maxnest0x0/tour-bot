from selenium.webdriver import Chrome, ChromeOptions

options = ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = Chrome(options)

driver.get("https://aviasales.ru/")

def get_token() -> str:
    return driver.get_cookie("_awt")["value"]
