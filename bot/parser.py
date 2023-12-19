import re
import datetime as dt

from ai.ai_parsers.city import CityParser, CityParserError
from ai.re_parsers.date import DateParser, DateParserError

class ParserError(Exception):
    pass

class TooLongTextError(ParserError):
    pass

class Parser:
    MAX_LENGTH = 100

    def __init__(self):
        self.city_parser = CityParser()
        self.date_parser = DateParser()

    async def parse(self, text, state):
        if len(text) > self.MAX_LENGTH:
            raise TooLongTextError("Text is too long")

        text = text.strip()
        text = re.sub(r"\s+", " ", text)

        city_res = await self.city_parser.parse(text)
        date_res = self.date_parser.parse(text)

        city_update = {key: value for key, value in city_res.items() if value is not None}
        date_update = {key: value for key, value in date_res.items() if value is not None}

        new_state = state.copy()
        new_state.update(city_update)
        new_state.update(date_update)

        self._validate_state(new_state)
        state.update(new_state)

    def get_missing_keys(self, state):
        keys = []
        for key in ("origin", "destination", "start"):
            if state[key] is None:
                keys.append(key)

        return keys

    def _validate_state(self, state):
        today = dt.datetime.now(dt.timezone(dt.timedelta(hours=5))).date()
        max_date = today + dt.timedelta(365)

        if state["origin"] is not None and state["destination"] is not None:
            if state["origin"] == state["destination"]:
                raise CityParserError("Origin and destination city are the same")

        if state["start"] is not None:
            if state["start"] < today:
                raise DateParserError("Start date is in the past")

            if state["start"] >= max_date:
                raise DateParserError("Start date is too far in the future")

        if state["end"] is not None:
            if state["end"] < today:
                raise DateParserError("End date is in the past")

            if state["end"] >= max_date:
                raise DateParserError("End date is too far in the future")

        if state["start"] is not None and state["end"] is not None:
            if state["end"] < state["start"]:
                raise DateParserError("End date is earlier than start date")
