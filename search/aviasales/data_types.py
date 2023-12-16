from typing import TypedDict, NotRequired, Sequence, Literal, Optional

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

class Badge(TypedDict):
    type: str
    name: str

class Price(TypedDict):
    default: int
    with_baggage: Optional[int]
    currency_code: str

class Airline(TypedDict):
    id: str
    name: str

class PlaceData(TypedDict):
    code: str
    name: str

class Place(TypedDict):
    airport: PlaceData
    city: PlaceData
    country: PlaceData

class Time(TypedDict):
    timestamp: int
    local_datetime: str

class Flight(TypedDict):
    seats_available: Optional[int]
    airline: Airline
    origin: Place
    destination: Place
    departure: Time
    arrival: Time

class Segment(TypedDict):
    flights: list[Flight]

class Ticket(TypedDict):
    id: str
    tags: list[str]
    badge: Optional[Badge]
    price: Price
    segments: list[Segment]

class SearchResults(TypedDict):
    tickets: list[Ticket]

PlaceType = Literal["airport", "city", "country"]

class SuggestedPlace(TypedDict):
    type: PlaceType
    code: str
    name: str
