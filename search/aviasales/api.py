from __future__ import annotations
import requests
import functools
import asyncio as aio
from typing import Any, cast

from .browser import AviasalesBrowserAuth
from .data_types import SearchParams, SearchResults

@functools.wraps(requests.request)
async def arequest(*args: Any, **kwargs: Any) -> requests.Response:
    loop = aio.get_running_loop()
    func = functools.partial(requests.request, *args, **kwargs)

    return await loop.run_in_executor(None, func)

class AviasalesAPIError(Exception):
    pass

class AviasalesAPI:
    AVIASALES_DOMAIN = "aviasales.ru"
    SEARCH_START_ENDPOINT = f"https://tickets-api.{AVIASALES_DOMAIN}/search/v2/start"

    @staticmethod
    async def raw_request(endpoint: str, token: str, body: Any) -> requests.Response:
        headers = {
            "x-client-type": "web",
            "x-origin-cookie": f"_awt={token}",
            "cookie": "auid=i'm just a random string",
        }

        return await arequest("POST", endpoint, headers=headers, json=body)

    def __init__(self) -> None:
        self._browser = AviasalesBrowserAuth()
        self.update_token()

    def update_token(self) -> None:
        self.token = self._browser.get_token()

    async def request(self, endpoint: str, body: Any) -> Any:
        r = await self.raw_request(endpoint, self.token, body)

        if r.status_code == requests.codes.forbidden:
            self.update_token()
            r = await self.raw_request(endpoint, self.token, body)

        if r.status_code == requests.codes.forbidden:
            raise AviasalesAPIError("Auth error")

        try:
            r.raise_for_status()
        except requests.HTTPError as error:
            raise AviasalesAPIError("Bad HTTP status") from error

        try:
            res = r.json()
        except requests.JSONDecodeError as error:
            raise AviasalesAPIError("Invalid JSON") from error

        return res

    async def search_start(self, search_params: SearchParams, *, market_code: str="ru", currency_code: str="RUB", language: str="ru") -> SearchAPI:
        body = {
            "search_params": search_params,
            "marker": "direct",
            "market_code": market_code,
            "currency_code": currency_code,
            "languages": {language: 1},
            "client_features": {"badges": True},
        }

        res = await self.request(self.SEARCH_START_ENDPOINT, body)
        return SearchAPI(self, res, language)

class SearchAPI:
    SEARCH_RESULTS_ENDPOINT_PATTERN = "https://{}/search/v3/results"

    def __init__(self, api: AviasalesAPI, res: Any, language: str):
        self._api = api
        self._search_id = res["search_id"]
        self._results_domain = res["results_url"]
        self._language = language

    async def search_results(self, ticket_limit: int, *, wait_until_done: bool=True, wait_time: float=2) -> SearchResults:
        body = {"limit": ticket_limit, "search_id": self._search_id}

        endpoint = self.SEARCH_RESULTS_ENDPOINT_PATTERN.format(self._results_domain)
        res = await self._api.request(endpoint, body)

        if wait_until_done:
            while not self._is_search_done(res):
                await aio.sleep(wait_time)
                res = await self._api.request(endpoint, body)

        try:
            return cast(SearchResults, self._prepare_data(res))
        except Exception as error:
            raise AviasalesAPIError("Failed to prepare response data") from error

    def _is_search_done(self, res: Any) -> bool:
        if not res:
            return False

        chunk = res[0]
        return cast(bool, chunk["last_update_timestamp"] == 0)

    def _prepare_data(self, res: Any) -> Any:
        if res:
            chunk = res[0]
            self._airlines = chunk["airlines"]
            self._flight_legs = chunk["flight_legs"]
            self._places = chunk["places"]
            self._tickets = chunk["tickets"]
        else:
            self._tickets = []

        tickets_data = self._prepare_tickets_data()
        return tickets_data

    def _prepare_tickets_data(self) -> Any:
        tickets_data: Any = {"tickets": []}

        for ticket in self._tickets:
            ticket_metadata = self._prepare_ticket_metadata(ticket)
            complex_ticket_data = self._prepare_complex_ticket_data(ticket)

            ticket_data = {**ticket_metadata, **complex_ticket_data}
            tickets_data["tickets"].append(ticket_data)

        return tickets_data

    def _prepare_ticket_metadata(self, ticket: Any) -> Any:
        tags_data = ticket["tags"]

        badge_data = None
        if "badges" in ticket:
            badge = ticket["badges"][0]
            badge_type = badge["type"]
            badge_name = badge["meta"]["name"][self._language]

            badge_data = {"type": badge_type, "name": badge_name}

        proposals = ticket["proposals"]
        cheapest_proposal = proposals[0]
        default_price = cheapest_proposal["price"]["value"]
        currency_code = cheapest_proposal["price"]["currency_code"]

        def check_for_baggage(proposal: Any) -> bool:
            baggage = proposal["minimum_fare"]["baggage"]
            return baggage is not None and baggage["count"] > 0

        price_with_baggage = None
        proposals_with_baggage = [proposal for proposal in proposals if check_for_baggage(proposal)]
        if proposals_with_baggage:
            cheapest_proposal_with_baggage = proposals_with_baggage[0]
            price_with_baggage = cheapest_proposal_with_baggage["price"]["value"]

        price_data = {"default": default_price, "with_baggage": price_with_baggage, "currency_code": currency_code}

        ticket_metadata = {
            "tags": tags_data,
            "badge": badge_data,
            "price": price_data,
        }

        return ticket_metadata

    def _prepare_complex_ticket_data(self, ticket: Any) -> Any:
        complex_ticket_data: Any = {"segments": []}
        cheapest_proposal = ticket["proposals"][0]

        for segment in ticket["segments"]:
            segment_data: Any = {"flights": []}
            flight_terms = [cheapest_proposal["flight_terms"][str(flight_index)] for flight_index in segment["flights"]]

            for flight_term in flight_terms:
                seats_available = None
                if "seats_available" in flight_term:
                    seats_available = flight_term["seats_available"]

                airline_id = flight_term["marketing_carrier_designator"]["airline_id"]
                airline_name = self._airlines[airline_id]["name"][self._language]["default"]
                airline_data = {"id": airline_id, "name": airline_name}

                number = flight_term["marketing_carrier_designator"]["number"]
                check_for_number = lambda flight_leg: flight_leg["operating_carrier_designator"]["number"] == number
                flight_leg = [flight_leg for flight_leg in self._flight_legs if check_for_number(flight_leg)][0]

                origin_data = self._prepare_place_data(flight_leg["origin"])
                destination_data = self._prepare_place_data(flight_leg["destination"])

                departure_timestamp = flight_leg["departure_unix_timestamp"]
                arrival_timestamp = flight_leg["arrival_unix_timestamp"]
                local_departure_datetime = flight_leg["local_departure_date_time"]
                local_arrival_datetime = flight_leg["local_arrival_date_time"]

                departure_data = {"timestamp": departure_timestamp, "local_datetime": local_departure_datetime}
                arrival_data = {"timestamp": arrival_timestamp, "local_datetime": local_arrival_datetime}

                flight_data = {
                    "seats_available": seats_available,
                    "airline": airline_data,
                    "origin": origin_data,
                    "destination": destination_data,
                    "departure": departure_data,
                    "arrival": arrival_data,
                }

                segment_data["flights"].append(flight_data)

            complex_ticket_data["segments"].append(segment_data)

        return complex_ticket_data

    def _prepare_place_data(self, airport_code: str) -> Any:
        airport = self._places["airports"][airport_code]
        airport_name = airport["name"][self._language]["default"]
        airport_data = {"code": airport_code, "name": airport_name}

        city_code = airport["city_code"]
        city = self._places["cities"][city_code]
        city_name = city["name"][self._language]["default"]
        city_data = {"code": city_code, "name": city_name}

        country_code = city["country"]
        country = self._places["countries"][country_code]
        country_name = country["name"][self._language]["default"]
        country_data = {"code": country_code, "name": country_name}

        place_data = {
            "airport": airport_data,
            "city": city_data,
            "country": country_data,
        }

        return place_data
