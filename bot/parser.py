import re
from typing import Final

from parsers.city import CityParser
from parsers.date import DateParser
from .data_types import InputParam, ParamsState

class ParserError(Exception):
    pass

class TooLongTextError(ParserError):
    pass

class InputParser:
    MAX_LENGTH: Final = 100
    REQUIRED_PARAMS: Final[tuple[InputParam, ...]] = ("origin", "destination", "start")

    def __init__(self) -> None:
        self.city_parser = CityParser()
        self.date_parser = DateParser()

    async def parse(self, text: str, state: ParamsState) -> ParamsState:
        if len(text) > self.MAX_LENGTH:
            raise TooLongTextError("Text is too long")

        text = text.strip()
        text = re.sub(r"\s+", " ", text)

        new_state = state
        new_state = await self.city_parser.parse(text, new_state)
        new_state = self.date_parser.parse(text, new_state)

        return new_state

    def get_missing_params(self, state: ParamsState) -> list[InputParam]:
        missing_params = []

        for param in self.REQUIRED_PARAMS:
            if state[param] is None:
                missing_params.append(param)

        return missing_params
