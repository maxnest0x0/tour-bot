import datetime as dt
from typing import Optional

from search.aviasales.api import AviasalesAPI
from .text import Text
from .data_types import ParamsState
from search.aviasales.data_types import SuggestedPlace, Direction, SearchResults

class TicketAggregator:
    def __init__(self) -> None:
        self.api = AviasalesAPI()

    async def search(self, state: ParamsState, ticket_limit: int=3, wait_max_retries: Optional[int]=3) -> str:
        assert state["origin"] is not None
        assert state["destination"] is not None
        assert state["start"] is not None

        directions = [self._get_direction(state["origin"], state["destination"], state["start"])]
        if state["end"] is not None:
            directions.append(self._get_direction(state["destination"], state["origin"], state["end"]))

        search = await self.api.search_start({
            "directions": directions,
            "passengers": {"adults": 1},
            "trip_class": "Y",
        })

        res = await search.search_results(ticket_limit, wait_max_retries)

        text = await self._generate_text(res)
        return text

    def _get_direction(self, origin: SuggestedPlace, destination: SuggestedPlace, date: dt.date) -> Direction:
        return {
            "origin": origin["code"],
            "destination": destination["code"],
            "date": date.isoformat(),
        }

    async def _generate_text(self, res: SearchResults) -> str:
        tickets = res["tickets"]
        if not tickets:
            return Text.no_tickets_found()

        text_paragraphs = []
        for ticket in tickets:
            ticket_lines = []

            badge = ticket["badge"]
            if badge is not None:
                ticket_lines.append(Text.badge(badge["name"]))

            price = ticket["price"]["default"]
            ticket_lines.append(Text.price(price))

            price_with_baggage = ticket["price"]["with_baggage"]
            if price_with_baggage is not None and price_with_baggage != price:
                ticket_lines.append(Text.price_with_baggage(price_with_baggage))

            for segment_idx, segment in enumerate(ticket["segments"]):
                if len(ticket["segments"]) == 2:
                    if segment_idx == 0:
                        ticket_lines.append(Text.to_there())
                    else:
                        ticket_lines.append(Text.from_there())

                for flight in segment["flights"]:
                    origin = Text.place(flight["origin"])
                    destination = Text.place(flight["destination"])

                    departure = Text.datetime(dt.datetime.fromisoformat(flight["departure"]["local_datetime"]))
                    arrival = Text.datetime(dt.datetime.fromisoformat(flight["arrival"]["local_datetime"]))

                    ticket_lines.append(Text.flight(origin, departure, destination, arrival))

            ticket_url = await self.api.shorten_url(self.api.get_ticket_url(ticket))
            ticket_lines.append(Text.link(ticket_url))

            text_paragraphs.append("\n".join(ticket_lines))

        text = Text.tickets_found() + "\n" + "\n\n".join(text_paragraphs)
        return text
