import requests
from .browser import AviasalesBrowserAuth
from typing import Any

class AviasalesAPIError(Exception):
    pass

class AviasalesAPI:
    AVIASALES_DOMAIN = "aviasales.ru"
    START_ENDPOINT = f"https://tickets-api.{AVIASALES_DOMAIN}/search/v2/start"

    @staticmethod
    def raw_request(endpoint: str, token: str, body: Any) -> requests.Response:
        headers = {
            "x-client-type": "web",
            "x-origin-cookie": f"_awt={token}",
            "cookie": "auid=i'm just a random string",
        }

        return requests.post(endpoint, headers=headers, json=body)

    def __init__(self) -> None:
        self._browser = AviasalesBrowserAuth()
        self.token = self._browser.get_token()

    def request(self, endpoint: str, body: Any) -> Any:
        r = self.raw_request(endpoint, self.token, body)

        if r.status_code == requests.codes.forbidden:
            self.token = self._browser.get_token()
            r = self.raw_request(endpoint, self.token, body)

        if r.status_code == requests.codes.forbidden:
            raise AviasalesAPIError("auth error")

        try:
            r.raise_for_status()
        except requests.HTTPError as error:
            raise AviasalesAPIError("bad HTTP status") from error

        try:
            return r.json()
        except requests.JSONDecodeError as error:
            raise AviasalesAPIError("invalid JSON") from error
