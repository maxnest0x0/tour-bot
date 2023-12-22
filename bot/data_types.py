import datetime as dt
from typing import TypedDict, Optional, NotRequired, Literal

from search.aviasales.data_types import SuggestedPlace

InputParam = Literal["origin", "destination", "start", "end"]

class ParamsState(TypedDict):
    origin: Optional[SuggestedPlace]
    destination: Optional[SuggestedPlace]
    start: Optional[dt.date]
    end: Optional[dt.date]

class ParamsStateUpdate(TypedDict):
    origin: NotRequired[Optional[SuggestedPlace]]
    destination: NotRequired[Optional[SuggestedPlace]]
    start: NotRequired[Optional[dt.date]]
    end: NotRequired[Optional[dt.date]]
