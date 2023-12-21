import datetime as dt
from enum import Enum
from typing import NamedTuple, Optional

class PrepositionType(Enum):
    START = 1
    END = 2

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
    preposition_type: Optional[PrepositionType]
    date_text_tuple: DateTextTuple

class DateWithPrepositionType(NamedTuple):
    preposition_type: Optional[PrepositionType]
    date: dt.date
