import re
import datetime as dt
from enum import Enum

class PrepositionType(Enum):
    START = 1
    END = 2

class DateParserError(Exception):
    pass

class DateParser:
    MONTHS = [
        "янв",
        "фев",
        "мар",
        "апр",
        "ма",
        "июн",
        "июл",
        "авг",
        "сен",
        "окт",
        "ноя",
        "дек",
    ]

    START_PREPOSITIONS = ["с", "со", "от"]
    END_PREPOSITIONS = ["по", "до"]

    def __init__(self):
        date_regexs = []

        long_day_regex = r"\d\d|\d"
        all_months_regex = "|".join(map(re.escape, self.MONTHS))
        long_month_regex = fr"({all_months_regex})[^ ]*"
        long_year_regex = r"\d\d\d\d"

        date_regexs.append(fr"(?:^|(?<= ))({long_day_regex}) {long_month_regex} ({long_year_regex})(?:$|(?=[г ]))")
        date_regexs.append(fr"(?:^|(?<= ))({long_day_regex}) {long_month_regex}(?:$|(?= ))")
        date_regexs.append(fr"(?:^|(?<= ))({long_day_regex}) числ")

        short_day_regex = r"\d\d|\d"
        short_month_regex = r"\d\d|\d"
        short_year_regex = r"\d\d\d\d|\d\d"

        date_regexs.append(fr"(?:^|(?<= ))({short_day_regex})\.({short_month_regex})\.({short_year_regex})(?:$|(?= ))")
        date_regexs.append(fr"(?:^|(?<= ))({short_day_regex})\.({short_month_regex})(?:$|(?= ))")

        self._date_regexs = [re.compile(regex, re.I) for regex in date_regexs]

    def parse(self, text):
        matches = self._find_dates(text)
        phrases = self._find_prepositions(matches, text)
        date_phrases = self._process_dates(phrases)
        res = self._decide_result(date_phrases)

        return res

    def _find_dates(self, text):
        found_spans = []
        matches = []

        for regex in self._date_regexs:
            for m in re.finditer(regex, text):
                for start, end in found_spans:
                    if max(start, m.start()) < min(end, m.end()):
                        break
                else:
                    found_spans.append(m.span())
                    matches.append(m)

        return matches

    def _find_prepositions(self, matches, text):
        phrases = []

        for m in matches:
            preposition_type = None
            words = text[:m.start()].split()

            if words:
                preposition = words[-1].lower()

                if preposition in self.START_PREPOSITIONS:
                    preposition_type = PrepositionType.START

                if preposition in self.END_PREPOSITIONS:
                    preposition_type = PrepositionType.END

            phrases.append((preposition_type, m))

        return phrases

    def _process_dates(self, phrases):
        date_phrases = []

        for preposition_type, m in phrases:
            prepared_date = self._prepare_date(m)
            translated_date = self._translate_date(*prepared_date)
            predicted_date = self._predict_date(*translated_date)
            date = dt.date(*reversed(predicted_date))

            date_phrases.append((preposition_type, date))

        return date_phrases

    def _decide_result(self, date_phrases):
        if len(date_phrases) > 2:
            raise DateParserError("Too many dates found")

        res = {"start": None, "end": None}
        dates_without_preposition = []

        for preposition_type, date in date_phrases:
            if preposition_type == PrepositionType.START:
                if res["start"] is not None:
                    raise DateParserError("Several start dates found")

                res["start"] = date

            if preposition_type == PrepositionType.END:
                if res["end"] is not None:
                    raise DateParserError("Several end dates found")

                res["end"] = date

            if preposition_type is None:
                dates_without_preposition.append(date)

        if len(dates_without_preposition) == 2:
            start, end = dates_without_preposition
            res["start"] = start
            res["end"] = end

        if len(dates_without_preposition) == 1:
            date = dates_without_preposition[0]

            if res["start"] is None:
                res["start"] = date
            elif res["end"] is None:
                res["end"] = date

        return res

    def _prepare_date(self, m):
        m_len = len(m.groups())

        day_text = m[1]

        month_text = None
        if m_len > 1:
            month_text = m[2]

        year_text = None
        if m_len > 2:
            year_text = m[3]

        return (day_text, month_text, year_text)

    def _translate_date(self, day_text, month_text=None, year_text=None):
        day = int(day_text)

        month = None
        if month_text is not None:
            month_text = month_text.lower()
            if month_text in self.MONTHS:
                month = self.MONTHS.index(month_text) + 1
            else:
                month = int(month_text)

        year = None
        if year_text is not None:
            year = int(year_text)
            if year < 100:
                year += 2000

        return (day, month, year)

    def _is_date_valid(self, day, month=None, year=None):
        if year is not None:
            try:
                dt.date(year, month, day)
            except ValueError:
                return False
        elif month is not None:
            try:
                dt.date(2024, month, day)
            except ValueError:
                return False
        else:
            try:
                dt.date(2024, 1, day)
            except ValueError:
                return False

        return True

    def _assert_date_valid(self, *args):
        if not self._is_date_valid(*args):
            raise DateParserError("Invalid date")

    def _is_date_in_past(self, today, day, month, year):
        if year < today.year:
            return True

        if year == today.year:
            if month < today.month:
                return True

            if month == today.month:
                if day < today.day:
                    return True

        return False

    def _predict_date(self, day, month=None, year=None):
        today = dt.datetime.now(dt.timezone(dt.timedelta(hours=5))).date()

        if year is not None:
            self._assert_date_valid(day, month, year)
            return (day, month, year)

        if month is not None:
            self._assert_date_valid(day, month)
            year = today.year

            while self._is_date_in_past(today, day, month, year) or not self._is_date_valid(day, month, year):
                year += 1

            return (day, month, year)

        self._assert_date_valid(day)
        year = today.year
        month = today.month

        while self._is_date_in_past(today, day, month, year) or not self._is_date_valid(day, month, year):
            month += 1

            if month > 12:
                month = 1
                year += 1

        return (day, month, year)
