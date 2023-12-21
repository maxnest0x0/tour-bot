import atexit
from selenium.webdriver import Chrome, ChromeOptions
from typing import Final, cast

class AviasalesBrowserAuthError(Exception):
    pass

class AviasalesBrowserAuth:
    AVIASALES_URL: Final = "https://aviasales.ru/"
    CHROME_ARGS: Final = [
        "--headless=new",
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]

    def __init__(self) -> None:
        atexit.register(self.quit)

        options = ChromeOptions()
        for arg in self.CHROME_ARGS:
            options.add_argument(arg)

        self._driver = Chrome(options)
        self._driver.get(self.AVIASALES_URL)

    def is_driver_alive(self) -> bool:
        try:
            self._driver.current_url
        except:
            return False

        return True

    def _assert_driver_alive(self) -> None:
        if not self.is_driver_alive():
            raise AviasalesBrowserAuthError("Browser is not running")

    def get_token(self) -> str:
        self._assert_driver_alive()

        cookie = self._driver.get_cookie("_awt")
        if cookie is None:
            raise AviasalesBrowserAuthError("Token cookie not found")

        return cast(str, cookie["value"])

    def refresh_page(self) -> None:
        self._assert_driver_alive()
        self._driver.refresh()

    def quit(self) -> None:
        self._driver.quit()
