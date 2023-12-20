import datetime as dt

class Text:
    KEYS = {
        "origin": "Город отправления",
        "destination": "Город прибытия",
        "start": "Дата отправления",
        "end": "Дата отправления обратно",
    }

    @staticmethod
    def tag(tag, text):
        return f"<{tag}>{text}</{tag}>"

    @staticmethod
    def nbsp():
        return "\N{NO-BREAK SPACE}"

    @staticmethod
    def rouble():
        return "₽"

    @staticmethod
    def arrow():
        return "→"

    @classmethod
    def keys(cls, keys):
        return ", ".join(cls.tag("i", key.lower() if i != 0 else key) for i, key in enumerate(keys))

    @classmethod
    def welcome(cls):
        p1 = "Привет! Скажите куда и когда вы хотите съездить, а я попытаюсь подобрать для вас билеты!"
        p2 = "Вот что мне нужно узнать:"
        p3 = cls.keys(cls.KEYS.values()) + " (если нужен обратный билет)"

        return "\n".join((p1, p2, p3))

    @staticmethod
    def processing_input():
        return "Обрабатываю ваш запрос..."

    @staticmethod
    def searching():
        p1 = "Ищу билеты по вашему запросу..."
        p2 = "Это займёт немного времени."

        return "\n".join((p1, p2))

    @staticmethod
    def busy():
        return "Пожалуйста, подождите, пока я работаю с предыдущим запросом."

    @staticmethod
    def tickets_found():
        return "Вот что мне удалось найти:"

    @staticmethod
    def no_tickets_found():
        p1 = "К сожалению, мне не удалось найти ни одного билета."
        p2 = "Может быть вам подойдёт другая дата или другой город?"

        return "\n".join((p1, p2))

    @staticmethod
    def date(date):
        day = str(date.day).rjust(2, "0")
        month = str(date.month).rjust(2, "0")
        year = str(date.year)

        return f"{day}.{month}.{year}"

    @classmethod
    def datetime(cls, datetime):
        day = str(datetime.day).rjust(2, "0")
        month = str(datetime.month).rjust(2, "0")
        year = str(datetime.year)

        hour = str(datetime.hour).rjust(2, "0")
        minute = str(datetime.minute).rjust(2, "0")

        return f"{day}.{month}.{year}{cls.nbsp()}{hour}:{minute}"

    @classmethod
    def current_state(cls, state):
        p1 = "Сейчас ваш запрос выглядит так:"

        text = []
        for key, value in state.items():
            key_text = cls.tag("i", cls.KEYS[key])

            if value is None:
                value_text = "?"
            elif isinstance(value, dt.date):
                value_text = cls.tag("b", cls.date(value))
            else:
                value_text = cls.tag("b", value["name"])

            text.append(f"{key_text}: {value_text}")

        return "\n".join((p1, *text))

    @classmethod
    def missing_keys(cls, keys):
        p1 = "Для того, чтобы я смог выполнить поиск, мне необходимо знать следующую информацию:"
        p2 = cls.keys(cls.KEYS[key] for key in keys)

        return "\n".join((p1, p2))

    @classmethod
    def badge(cls, badge):
        return cls.tag("b", f"{badge}!")

    @classmethod
    def price(cls, price):
        return cls.tag("i", "Цена") + ": " + cls.tag("b", price) + cls.nbsp() + cls.rouble()

    @classmethod
    def price_with_baggage(cls, price_with_baggage):
        return cls.tag("i", "Цена с багажом") + ": " + cls.tag("b", price_with_baggage) + cls.nbsp() + cls.rouble()

    @classmethod
    def to_there(cls):
        return cls.tag("u", "Туда:")

    @classmethod
    def from_there(cls):
        return cls.tag("u", "Обратно:")

    @classmethod
    def place(cls, place):
        city = place["city"]["name"]
        airport = place["airport"]["name"]

        if city == airport:
            return city

        return f"{city}, {airport}"

    @classmethod
    def flight(cls, origin, departure, destination, arrival):
        arrow = cls.nbsp() + cls.tag("b", cls.arrow()) + cls.nbsp()
        return f"{origin} ({departure}){arrow}{destination} ({arrival})"

    @classmethod
    def error_text(cls, error):
        return cls.tag("pre", error)

    @staticmethod
    def city_error():
        p1 = "Похоже, мне не удалось однозначно распознать название города/городов в вашем запросе!"
        p2 = "Пожалуйста, попробуйте переформулировать запрос."

        return "\n".join((p1, p2))

    @staticmethod
    def date_error():
        p1 = "Кажется, мне не удалось однозначно распознать дату/даты в вашем запросе!"
        p2 = "Пожалуйста, попробуйте переформулировать запрос."

        return "\n".join((p1, p2))

    @staticmethod
    def too_long_error():
        p1 = "Хмм, запрос слишком длинный и мне сложно понять его!"
        p2 = "Пожалуйста, попробуйте переформулировать запрос."

        return "\n".join((p1, p2))

    @staticmethod
    def unknown_error():
        p1 = "Ой, произошла неожиданная ошибка!"
        p2 = "Не беспокойтесь, мы обязательно исправим её до защиты."

        return "\n".join((p1, p2))
