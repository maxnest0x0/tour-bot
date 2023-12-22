import datetime as dt
from enum import Enum
from typing import NamedTuple, Optional

from search.aviasales.data_types import SuggestedPlace

class CityPrepositionType(Enum):
    ORIGIN = 1
    DESTINATION = 2

class DatePrepositionType(Enum):
    START = 1
    END = 2

class LocationWithPrepositionType(NamedTuple):
    preposition_type: Optional[CityPrepositionType]
    name: str

class CityWithPrepositionType(NamedTuple):
    preposition_type: Optional[CityPrepositionType]
    city: SuggestedPlace

class DateTextTuple(NamedTuple):
    day_text: str
    month_text: Optional[str] = None
    year_text: Optional[str] = None

class DateTuple(NamedTuple):
    day: int
    month: Optional[int] = None
    year: Optional[int] = None

class FilledDateTuple(NamedTuple):
    day: int
    month: int
    year: int

class DateTextTupleWithIndex(NamedTuple):
    idx: int
    date_text_tuple: DateTextTuple

class DateTextTupleWithPrepositionType(NamedTuple):
    preposition_type: Optional[DatePrepositionType]
    date_text_tuple: DateTextTuple

class DateWithPrepositionType(NamedTuple):
    preposition_type: Optional[DatePrepositionType]
    date: dt.date
