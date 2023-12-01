from typing import TypedDict, NotRequired, Sequence, Literal

class Direction(TypedDict):
    origin: str
    destination: str
    date: str

class Passengers(TypedDict):
    adults: int
    children: NotRequired[int]
    infants: NotRequired[int]

TripClass = Literal["Y", "W", "C", "F"]

class SearchParams(TypedDict):
    directions: Sequence[Direction]
    passengers: Passengers
    trip_class: TripClass
