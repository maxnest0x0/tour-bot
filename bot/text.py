import datetime as dt
from emoji import emojize as emj
from typing import Final, Iterable, cast

from .data_types import ParamsState, InputParam
from search.aviasales.data_types import SuggestedPlace, Place

class Text:
    PARAMS: Final = {
        "origin": "Город отправления",
        "destination": "Город прибытия",
        "start": "Дата отправления",
        "end": "Дата отправления обратно",
    }

    @staticmethod
    def nbsp() -> str:
        return "\N{NO-BREAK SPACE}"

    @staticmethod
    def rouble() -> str:
        return "₽"

    @staticmethod
    def arrow() -> str:
        return "→"

    @staticmethod
    def tag(tag: str, text: str) -> str:
        return f"<{tag}>{text}</{tag}>"

    @classmethod
    def params(cls, params: Iterable[str]) -> str:
        return ", ".join(cls.tag("i", param.lower() if idx != 0 else param) for idx, param in enumerate(params))

    @staticmethod
    def date(date: dt.date) -> str:
        day = str(date.day).rjust(2, "0")
        month = str(date.month).rjust(2, "0")
        year = str(date.year)

        return f"{day}.{month}.{year}"

    @classmethod
    def datetime(cls, datetime: dt.datetime) -> str:
        day = str(datetime.day).rjust(2, "0")
        month = str(datetime.month).rjust(2, "0")
        year = str(datetime.year)

        hour = str(datetime.hour).rjust(2, "0")
        minute = str(datetime.minute).rjust(2, "0")

        return f"{day}.{month}.{year}{cls.nbsp()}{hour}:{minute}"

    @classmethod
    def welcome(cls) -> str:
        line1 = ":waving_hand: Привет! Скажите куда и когда вы хотите съездить, а я попытаюсь подобрать для вас билеты!"
        line2 = "Вот что мне нужно узнать:"
        line3 = cls.params(cls.PARAMS.values()) + " (если нужен обратный билет)"

        return emj("\n".join((line1, line2, line3)))

    @staticmethod
    def processing_input() -> str:
        return emj(":thinking_face: Обрабатываю ваш запрос...")

    @staticmethod
    def searching() -> str:
        line1 = ":magnifying_glass_tilted_right: Ищу билеты по вашему запросу..."
        line2 = "Это займёт немного времени."

        return emj("\n".join((line1, line2)))

    @staticmethod
    def busy() -> str:
        return emj(":hourglass_not_done: Пожалуйста, подождите, пока я работаю с предыдущим запросом.")

    @staticmethod
    def tickets_found() -> str:
        return emj(":ticket: Вот, что мне удалось найти:")

    @staticmethod
    def no_tickets_found() -> str:
        line1 = ":neutral_face: К сожалению, мне не удалось найти ни одного билета."
        line2 = "Может быть вам подойдёт другая дата или другой город?"

        return emj("\n".join((line1, line2)))

    @classmethod
    def params_state(cls, state: ParamsState) -> str:
        line1 = ":airplane: Сейчас ваш запрос выглядит так:"

        lines = []
        for param, value in state.items():
            param_text = cls.tag("i", cls.PARAMS[param])

            if value is None:
                value_text = "?"
            elif isinstance(value, dt.date):
                value_text = cls.tag("b", cls.date(value))
            else:
                value_text = cls.tag("b", cast(SuggestedPlace, value)["name"])

            lines.append(f"{param_text}: {value_text}")

        return emj("\n".join((line1, *lines)))

    @classmethod
    def missing_params(cls, params: Iterable[InputParam]) -> str:
        line1 = ":red_question_mark: Для того, чтобы выполнить поиск, мне необходимо знать следующую информацию:"
        line2 = cls.params(cls.PARAMS[param] for param in params)

        return emj("\n".join((line1, line2)))

    @classmethod
    def badge(cls, name: str) -> str:
        return emj(":smiling_face_with_sunglasses: " + cls.tag("b", f"{name}!"))

    @classmethod
    def price(cls, price: int) -> str:
        return emj(":money_bag: " + cls.tag("i", "Цена") + ": " + cls.tag("b", str(price)) + cls.nbsp() + cls.rouble())

    @classmethod
    def price_with_baggage(cls, price: int) -> str:
        return emj(":luggage: " + cls.tag("i", "Цена с багажом") + ": " + cls.tag("b", str(price)) + cls.nbsp() + cls.rouble())

    @classmethod
    def to_there(cls) -> str:
        return emj(":airplane_departure: " + cls.tag("u", "Туда:"))

    @classmethod
    def from_there(cls) -> str:
        return emj(":airplane_arrival: " + cls.tag("u", "Обратно:"))

    @staticmethod
    def place(place: Place) -> str:
        city = place["city"]["name"]
        airport = place["airport"]["name"]

        if city == airport:
            return city

        return f"{city}, {airport}"

    @classmethod
    def flight(cls, origin: str, departure: str, destination: str, arrival: str) -> str:
        arrow = cls.nbsp() + cls.tag("b", cls.arrow()) + cls.nbsp()
        return f"{origin} ({departure}){arrow}{destination} ({arrival})"

    @staticmethod
    def link(url: str) -> str:
        return emj(":link: " + url)

    @classmethod
    def error_text(cls, text: str) -> str:
        return emj(":prohibited: " + cls.tag("code", text))

    @staticmethod
    def repeat_input() -> str:
        return "Пожалуйста, попробуйте переформулировать запрос."

    @classmethod
    def city_error(cls) -> str:
        line1 = ":cityscape: Похоже, мне не удалось однозначно распознать название города/городов в вашем запросе!"
        line2 = cls.repeat_input()

        return emj("\n".join((line1, line2)))

    @classmethod
    def date_error(cls) -> str:
        line1 = ":calendar: Кажется, мне не удалось однозначно распознать дату/даты в вашем запросе!"
        line2 = cls.repeat_input()

        return emj("\n".join((line1, line2)))

    @classmethod
    def too_long_error(cls) -> str:
        line1 = ":exploding_head: Хмм, запрос слишком длинный и мне сложно понять его!"
        line2 = cls.repeat_input()

        return emj("\n".join((line1, line2)))

    @staticmethod
    def unknown_error() -> str:
        line1 = ":face_screaming_in_fear: Ой, произошла неожиданная ошибка!"
        line2 = "Не беспокойтесь, мы скоро её исправим."

        return emj("\n".join((line1, line2)))
