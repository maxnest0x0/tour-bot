import spacy
from enum import Enum

from search.aviasales.api import AviasalesAPI, AviasalesAPIError

class PrepositionType(Enum):
    ORIGIN = 1
    DESTINATION = 2

class CityParserError(Exception):
    pass

class CityParser:
    NER_LABELS = ["LOC"]
    ORIGIN_PREPOSITIONS = ["из", "с", "со", "от"]
    DESTINATION_PREPOSITIONS = ["в", "во", "на", "к", "до"]

    def __init__(self, model_name="ru_core_news_sm"):
        self._model = spacy.load(model_name)

    async def parse(self, text, state):
        prepared_text = self._prepare_text(text)
        ents = self._get_named_entities(prepared_text)
        locations_with_preposition_type = self._find_prepositions(ents)
        cities_with_preposition_type = await self._process_cities(locations_with_preposition_type)
        res = self._decide_result(cities_with_preposition_type, state)

        return res

    def _prepare_text(self, text):
        max_len = max(len(word) for word in self.ORIGIN_PREPOSITIONS + self.DESTINATION_PREPOSITIONS)
        words = []

        for word in text.split():
            if len(word) > max_len:
                word = word[0].upper() + word[1:]

            words.append(word)

        return " ".join(words)

    def _get_named_entities(self, text):
        doc = self._model(text)
        ents = [ent for ent in doc.ents if ent.label_ in self.NER_LABELS]
        return ents

    def _find_prepositions(self, ents):
        locations_with_preposition_type = []

        for ent in ents:
            preposition_type = None

            if ent.start > 0:
                preposition = ent.doc[ent.start - 1].lower_

                if preposition in self.ORIGIN_PREPOSITIONS:
                    preposition_type = PrepositionType.ORIGIN

                if preposition in self.DESTINATION_PREPOSITIONS:
                    preposition_type = PrepositionType.DESTINATION

            locations_with_preposition_type.append((preposition_type, ent.text))

        return locations_with_preposition_type

    async def _process_cities(self, locations_with_preposition_type):
        cities_with_preposition_type = []

        for preposition_type, name in locations_with_preposition_type:
            try:
                places = await AviasalesAPI.suggest_places(name, 2)
            except AviasalesAPIError:
                continue

            if not places:
                continue

            place = places[0]
            if place["type"] != "city":
                continue

            cities_with_preposition_type.append((preposition_type, place))

        return cities_with_preposition_type

    def _decide_result(self, cities_with_preposition_type, state):
        if len(cities_with_preposition_type) > 2:
            raise CityParserError("Too many cities found")

        res = {"origin": None, "destination": None}
        cities_without_preposition = []

        for preposition_type, city in cities_with_preposition_type:
            if preposition_type == PrepositionType.ORIGIN:
                if res["origin"] is not None:
                    raise CityParserError("Several origin cities found")

                res["origin"] = city

            if preposition_type == PrepositionType.DESTINATION:
                if res["destination"] is not None:
                    raise CityParserError("Several destination cities found")

                res["destination"] = city

            if preposition_type is None:
                cities_without_preposition.append(city)

        if len(cities_without_preposition) == 2:
            origin, destination = cities_without_preposition
            res["origin"] = origin
            res["destination"] = destination

        if len(cities_without_preposition) == 1:
            city = cities_without_preposition[0]

            if res["origin"] is not None:
                res["destination"] = city
            elif res["destination"] is not None:
                res["origin"] = city
            elif state["origin"] is not None:
                res["destination"] = city
            elif state["destination"] is not None:
                res["origin"] = city
            else:
                res["destination"] = city

        return res
