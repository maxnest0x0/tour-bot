from enum import Enum
from typing import NamedTuple, Optional

from search.aviasales.data_types import SuggestedPlace

class PrepositionType(Enum):
    ORIGIN = 1
    DESTINATION = 2

class LocationWithPrepositionType(NamedTuple):
    preposition_type: Optional[PrepositionType]
    name: str

class CityWithPrepositionType(NamedTuple):
    preposition_type: Optional[PrepositionType]
    city: SuggestedPlace
