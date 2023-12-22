import datetime as dt
from typing import TypedDict, Optional, NotRequired

from search.aviasales.data_types import SuggestedPlace

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
