import datetime as dt

from search.aviasales.api import AviasalesAPI
from .text import Text

class TicketsSearch:
    api = AviasalesAPI()

    async def search(self, state):
        directions = [{
            "origin": state["origin"]["code"],
            "destination": state["destination"]["code"],
            "date": state["start"].isoformat(),
        }]

        if state["end"] is not None:
            directions.append({
                "origin": state["destination"]["code"],
                "destination": state["origin"]["code"],
                "date": state["end"].isoformat(),
            })

        search = await self.api.search_start({
            "directions": directions,
            "passengers": {"adults": 1},
            "trip_class": "Y",
        })

        res = await search.search_results(3, 3)
        return res

    async def make_text(self, res):
        tickets = res["tickets"]
        if not tickets:
            return Text.no_tickets_found()

        text = []
        for ticket in tickets:
            ticket_text = []

            badge = ticket["badge"]
            if badge is not None:
                ticket_text.append(Text.badge(badge["name"]))

            price = ticket["price"]["default"]
            ticket_text.append(Text.price(price))

            price_with_baggage = ticket["price"]["with_baggage"]
            if price_with_baggage is not None and price_with_baggage != price:
                ticket_text.append(Text.price_with_baggage(price_with_baggage))

            segment_index = 0
            for i, segment in enumerate(ticket["segments"]):
                if len(ticket["segments"]) == 2:
                    if i == 0:
                        ticket_text.append(Text.to_there())
                    else:
                        ticket_text.append(Text.from_there())

                for flight in segment["flights"]:
                    origin = Text.place(flight["origin"])
                    destination = Text.place(flight["destination"])

                    departure = Text.datetime(dt.datetime.fromisoformat(flight["departure"]["local_datetime"]))
                    arrival = Text.datetime(dt.datetime.fromisoformat(flight["arrival"]["local_datetime"]))

                    ticket_text.append(Text.flight(origin, departure, destination, arrival))

            ticket_url = await self.api.shorten_url(self.api.get_ticket_url(ticket))
            ticket_text.append(ticket_url)

            text.append("\n".join(ticket_text))

        return "\n\n".join(text)
