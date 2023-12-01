from __future__ import annotations

import requests
from typing import Any

from .browser import AviasalesBrowserAuth
from .data_types import SearchStartRequestData

class AviasalesAPIError(Exception):
    pass

class AviasalesAPI:
    AVIASALES_DOMAIN = "aviasales.ru"
    SEARCH_START_ENDPOINT = f"https://tickets-api.{AVIASALES_DOMAIN}/search/v2/start"

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
        self.update_token()

    def update_token(self) -> None:
        self.token = self._browser.get_token()

    def request(self, endpoint: str, body: Any) -> Any:
        r = self.raw_request(endpoint, self.token, body)

        if r.status_code == requests.codes.forbidden:
            self.update_token()
            r = self.raw_request(endpoint, self.token, body)

        if r.status_code == requests.codes.forbidden:
            raise AviasalesAPIError("Auth error")

        try:
            r.raise_for_status()
        except requests.HTTPError as error:
            raise AviasalesAPIError("Bad HTTP status") from error

        try:
            return r.json()
        except requests.JSONDecodeError as error:
            raise AviasalesAPIError("Invalid JSON") from error

    def search_start(self, data: SearchStartRequestData) -> SearchAPI:
        body = {
            "search_params": data,
            "marker": "direct",
            "market_code": "ru",
            "currency_code": "rub",
            "languages": {
                "ru": 1,
            },
        }

        res = self.request(self.SEARCH_START_ENDPOINT, body)
        return SearchAPI(self, res)

class SearchAPI:
    SEARCH_RESULTS_ENDPOINT_TEMPLATE = "https://{}/search/v3/results"

    def __init__(self, api: AviasalesAPI, res: Any):
        self._api = api
        self.search_id = res["search_id"]
        self.results_domain = res["results_url"]

    def search_results(self, data):
        body = {**data, "search_id": self.search_id}

        endpoint = self.SEARCH_RESULTS_ENDPOINT_TEMPLATE.format(self.results_domain)
        res = self._api.request(endpoint, body)

        return self._prepare_data(res)

    def _prepare_data(self, res):
        chunk = res[0]

        self._airlines = chunk["airlines"]
        self._flight_legs = chunk["flight_legs"]
        self._places = chunk["places"]
        self._tickets = chunk["tickets"]

        tickets_data = self._prepare_tickets_data()
        return tickets_data

    def _prepare_tickets_data(self):
        tickets_data = {"tickets": []}

        for ticket in self._tickets:
            ticket_metadata = self._prepare_ticket_metadata(ticket)
            complex_ticket_data = self._prepare_complex_ticket_data(ticket)

            ticket_data = {**ticket_metadata, **complex_ticket_data}
            tickets_data["tickets"].append(ticket_data)

        return tickets_data

    def _prepare_ticket_metadata(self, ticket):
        tags_data = ticket["tags"]

        badge_data = None
        if "badges" in ticket:
            badge = ticket["badges"][0]
            badge_type = badge["type"]
            badge_name = badge["meta"]["name"]["ru"]

            badge_data = {"type": badge_type, "name": badge_name}

        proposals = ticket["proposals"]
        cheapest_proposal = proposals[0]
        default_price = cheapest_proposal["price"]["value"]

        price_with_baggage = None
        def check_for_baggage(proposal):
            baggage = proposal["minimum_fare"]["baggage"]
            return baggage is not None and baggage["count"] > 0
        proposals_with_baggage = [proposal for proposal in proposals if check_for_baggage(proposal)]
        if proposals_with_baggage:
            cheapest_proposal_with_baggage = proposals_with_baggage[0]
            price_with_baggage = cheapest_proposal_with_baggage["price"]["value"]

        price_data = {"default": default_price, "with_baggage": price_with_baggage}

        ticket_metadata = {
            "tags": tags_data,
            "badge": badge_data,
            "price": price_data,
        }
        return ticket_metadata

    def _prepare_complex_ticket_data(self, ticket):
        complex_ticket_data = {"segments": []}
        cheapest_proposal = ticket["proposals"][0]
        for segment in ticket["segments"]:
            segment_data = {"flights": []}
            flight_terms = [cheapest_proposal["flight_terms"][str(flight_index)] for flight_index in segment["flights"]]
            for flight_term in flight_terms:
                seats_available = None
                if "seats_available" in flight_term:
                    seats_available = flight_term["seats_available"]

                airline_id = flight_term["marketing_carrier_designator"]["airline_id"]
                airline_name = self._airlines[airline_id]["name"]["ru"]["default"]
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

    def _prepare_place_data(self, airport_code):
        airport = self._places["airports"][airport_code]
        airport_name = airport["name"]["ru"]["default"]
        airport_data = {"code": airport_code, "name": airport_name}

        city_code = airport["city_code"]
        city = self._places["cities"][city_code]
        city_name = city["name"]["ru"]["default"]
        city_data = {"code": city_code, "name": city_name}

        country_code = city["country"]
        country = self._places["countries"][country_code]
        country_name = country["name"]["ru"]["default"]
        country_data = {"code": country_code, "name": country_name}

        place_data = {
            "airport": airport_data,
            "city": city_data,
            "country": country_data,
        }
        return place_data
