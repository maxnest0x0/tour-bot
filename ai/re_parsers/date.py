import re
import datetime as dt
from typing import Final, Sequence

from .data_types import *
from bot.data_types import ParamsState, ParamsStateUpdate

class DateParserError(Exception):
    pass

class DateParser:
    TIMEZONE: Final = dt.timezone(dt.timedelta(hours=5))

    MONTHS: Final = [
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
    MONTH_PLACEHOLDER: Final = "числ"
    YEAR_ENDING: Final = "г"

    START_PREPOSITIONS: Final = ["с", "со", "от"]
    END_PREPOSITIONS: Final = ["по", "до"]

    def __init__(self) -> None:
        all_months = r"|".join(map(re.escape, self.MONTHS))
        default_start = r"(?:^|(?<= ))"
        default_end = r"(?:$|(?= ))"
        year_end = default_end.replace(r" ", fr"[{re.escape(self.YEAR_ENDING)} ]")
        empty_group = r"()"

        long_day = r"(\d\d|\d)"
        long_month = fr"({all_months})[^ ]*"
        long_year = r"(\d\d\d\d)"

        short_day = r"(\d\d|\d)"
        short_month = r"(\d\d|\d)"
        short_year = r"(\d\d\d\d|\d\d)"

        date_options = [
            fr"{default_start}{long_day} {long_month} {long_year}{year_end}",
            fr"{default_start}{long_day} {long_month}{default_end}{empty_group}",
            fr"{default_start}{long_day} {re.escape(self.MONTH_PLACEHOLDER)}{empty_group * 2}",
            fr"{default_start}{short_day}\.{short_month}\.{short_year}{default_end}",
            fr"{default_start}{short_day}\.{short_month}{default_end}{empty_group}",
        ]
        self._date_options_num = len(date_options)

        date_regexp = r"|".join(date_options)
        self._date_regexp = re.compile(date_regexp, re.IGNORECASE)

    def parse(self, text: str, state: ParamsState) -> ParamsStateUpdate:
        date_text_tuples_with_index = self._find_dates(text)
        date_text_tuples_with_preposition_type = self._find_prepositions(date_text_tuples_with_index, text)
        dates_with_preposition_type = self._process_dates(date_text_tuples_with_preposition_type)
        res = self._decide_result(dates_with_preposition_type, state)

        return res

    def _find_dates(self, text: str) -> list[DateTextTupleWithIndex]:
        date_text_tuples_with_index = []

        for m in re.finditer(self._date_regexp, text):
            for group_idx in range(1, self._date_options_num * 3, 3):
                day_text = m[group_idx] or None
                month_text = m[group_idx + 1] or None
                year_text = m[group_idx + 2] or None

                if day_text is not None:
                    date_text_tuple = DateTextTuple(day_text, month_text, year_text)
                    date_text_tuples_with_index.append(DateTextTupleWithIndex(m.start(), date_text_tuple))

        return date_text_tuples_with_index

    def _find_prepositions(self, date_text_tuples_with_index: Sequence[DateTextTupleWithIndex], text: str) -> list[DateTextTupleWithPrepositionType]:
        date_text_tuples_with_preposition_type = []

        for idx, date_text_tuple in date_text_tuples_with_index:
            preposition_type = None
            words = text[:idx].split()

            if words:
                preposition = words[-1].lower()

                if preposition in self.START_PREPOSITIONS:
                    preposition_type = PrepositionType.START

                if preposition in self.END_PREPOSITIONS:
                    preposition_type = PrepositionType.END

            date_text_tuples_with_preposition_type.append(DateTextTupleWithPrepositionType(preposition_type, date_text_tuple))

        return date_text_tuples_with_preposition_type

    def _process_dates(self, date_text_tuples_with_preposition_type: Sequence[DateTextTupleWithPrepositionType]) -> list[DateWithPrepositionType]:
        dates_with_preposition_type = []

        for preposition_type, date_text_tuple in date_text_tuples_with_preposition_type:
            translated_date_tuple = self._translate_date(date_text_tuple)
            predicted_date_tuple = self._predict_date(translated_date_tuple)
            date = dt.date(*reversed(predicted_date_tuple))

            dates_with_preposition_type.append(DateWithPrepositionType(preposition_type, date))

        return dates_with_preposition_type

    def _decide_result(self, dates_with_preposition_type: Sequence[DateWithPrepositionType], state: ParamsState) -> ParamsStateUpdate:
        if len(dates_with_preposition_type) > 2:
            raise DateParserError("Too many dates found")

        res: ParamsStateUpdate = {"start": None, "end": None}
        dates_without_preposition = []

        for preposition_type, date in dates_with_preposition_type:
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

            if res["end"] is not None:
                res["start"] = date
            elif res["start"] is not None:
                res["end"] = date
            elif state["end"] is not None:
                res["start"] = date
            elif state["start"] is not None:
                res["end"] = date
            else:
                res["start"] = date

        return res

    def _translate_date(self, date_text_tuple: DateTextTuple) -> DateTuple:
        day_text, month_text, year_text = date_text_tuple

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

            if len(year_text) == 2:
                year += 2000

        return DateTuple(day, month, year)

    def _is_date_valid(self, date_tuple: DateTuple) -> bool:
        day, month, year = date_tuple

        if year is not None:
            assert month is not None
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

    def _assert_date_valid(self, date_tuple: DateTuple) -> None:
        if not self._is_date_valid(date_tuple):
            raise DateParserError("Invalid date")

    def _get_today_date(self) -> dt.date:
        return dt.datetime.now(self.TIMEZONE).date()

    def _is_date_not_in_past(self, date_tuple: FilledDateTuple) -> bool:
        date = dt.date(*reversed(date_tuple))
        return date >= self._get_today_date()

    def _predict_date(self, date_tuple: DateTuple) -> FilledDateTuple:
        day, month, year = date_tuple
        today = self._get_today_date()

        if year is not None:
            self._assert_date_valid(DateTuple(day, month, year))
            assert month is not None
            return FilledDateTuple(day, month, year)

        if month is not None:
            self._assert_date_valid(DateTuple(day, month))
            year = today.year

            while True:
                if self._is_date_valid(DateTuple(day, month, year)):
                    if self._is_date_not_in_past(FilledDateTuple(day, month, year)):
                        break

                year += 1

            return FilledDateTuple(day, month, year)

        self._assert_date_valid(DateTuple(day))
        year = today.year
        month = today.month

        while True:
            if self._is_date_valid(DateTuple(day, month, year)):
                if self._is_date_not_in_past(FilledDateTuple(day, month, year)):
                    break

            month += 1
            if month > 12:
                month = 1
                year += 1

        return FilledDateTuple(day, month, year)
