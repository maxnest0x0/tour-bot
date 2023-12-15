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

    async def parse(self, text):
        prepared_text = self._prepare_text(text)
        ents = self._get_named_entities(prepared_text)
        phrases = self._find_prepositions(ents)
        city_phrases = await self._process_cities(phrases)
        res = self._decide_result(city_phrases)

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
        phrases = []

        for ent in ents:
            preposition_type = None

            if ent.start > 0:
                preposition = ent.doc[ent.start - 1].lower_
                preposition_type = self._get_preposition_type(preposition)

                if preposition_type is None and ent.start > 1:
                    preposition = ent.doc[ent.start - 2].lower_
                    preposition_type = self._get_preposition_type(preposition)

            phrases.append((preposition_type, ent.text))

        return phrases

    def _get_preposition_type(self, preposition):
        preposition_type = None

        if preposition in self.ORIGIN_PREPOSITIONS:
            preposition_type = PrepositionType.ORIGIN

        if preposition in self.DESTINATION_PREPOSITIONS:
            preposition_type = PrepositionType.DESTINATION

        return preposition_type

    async def _process_cities(self, phrases):
        city_phrases = []

        for preposition_type, name in phrases:
            try:
                places = await AviasalesAPI.suggest_places(name, 1)
            except AviasalesAPIError:
                continue

            if not places:
                continue

            place = places[0]
            if place["type"] != "city":
                continue

            city_phrases.append((preposition_type, place["code"]))

        return city_phrases

    def _decide_result(self, city_phrases):
        if len(city_phrases) > 2:
            raise CityParserError("Too many cities found")

        res = {"origin": None, "destination": None}
        cities_without_preposition = []

        for preposition_type, code in city_phrases:
            if preposition_type == PrepositionType.ORIGIN:
                if res["origin"] is not None:
                    raise CityParserError("Several origin cities found")

                res["origin"] = code

            if preposition_type == PrepositionType.DESTINATION:
                if res["destination"] is not None:
                    raise CityParserError("Several destination cities found")

                res["destination"] = code

            if preposition_type is None:
                cities_without_preposition.append(code)

        if len(cities_without_preposition) == 2:
            origin, destination = cities_without_preposition
            res["origin"] = origin
            res["destination"] = destination

        if len(cities_without_preposition) == 1:
            code = cities_without_preposition[0]

            if res["destination"] is None:
                res["destination"] = code
            elif res["origin"] is None:
                res["origin"] = code

        return res
