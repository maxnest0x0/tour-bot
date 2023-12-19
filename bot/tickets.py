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
                ticket_text.append(badge["name"] + "!")

            price = ticket["price"]["default"]
            ticket_text.append(f"Цена: {price} ₽")

            price_with_baggage = ticket["price"]["with_baggage"]
            if price_with_baggage is not None and price_with_baggage != price:
                ticket_text.append(f"Цена с багажом: {price_with_baggage} ₽")

            segment_index = 0
            for segment in ticket["segments"]:
                if len(ticket["segments"]) == 2:
                    if segment_index == 0:
                        ticket_text.append("Туда:")
                    else:
                        ticket_text.append("Обратно:")

                for flight in segment["flights"]:
                    origin = flight["origin"]
                    origin_text = origin["city"]["name"]
                    if origin["city"]["name"] != origin["airport"]["name"]:
                        origin_text += ", " + origin["airport"]["name"]

                    destination = flight["destination"]
                    destination_text = destination["city"]["name"]
                    if destination["city"]["name"] != destination["airport"]["name"]:
                        destination_text += ", " + destination["airport"]["name"]

                    departure = dt.datetime.fromisoformat(flight["departure"]["local_datetime"])
                    departure_data = [str(getattr(departure, attr)).rjust(2, "0") for attr in ("day", "month", "year", "hour", "minute")]
                    departure_text = f"{departure_data[0]}.{departure_data[1]}.{departure_data[2]} {departure_data[3]}:{departure_data[4]}"

                    arrival = dt.datetime.fromisoformat(flight["arrival"]["local_datetime"])
                    arrival_data = [str(getattr(arrival, attr)).rjust(2, "0") for attr in ("day", "month", "year", "hour", "minute")]
                    arrival_text = f"{arrival_data[0]}.{arrival_data[1]}.{arrival_data[2]} {arrival_data[3]}:{arrival_data[4]}"

                    ticket_text.append(f"{origin_text} ({departure_text}) → {destination_text} ({arrival_text})")

                segment_index += 1

            ticket_url = await self.api.shorten_url(self.api.get_ticket_url(ticket))
            ticket_text.append(ticket_url)

            text.append("\n".join(ticket_text))

        return "\n\n".join(text)
