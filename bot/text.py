class Text:
    KEYS = {
        "origin": "Город отправления",
        "destination": "Город прибытия",
        "start": "Дата отправления",
        "end": "Дата отправления обратно",
    }

    @classmethod
    def welcome(cls):
        p1 = "Привет! Скажите куда и когда вы хотите съездить, а я попытаюсь подобрать для вас билеты!"
        p2 = "Вот что мне нужно узнать:"
        p3 = ", ".join(cls.KEYS.values()) + " (если нужен обратный билет)"

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
    def tickets_found():
        return "Вот что мне удалось найти:"

    @staticmethod
    def no_tickets_found():
        p1 = "К сожалению, мне не удалось найти ни одного билета."
        p2 = "Может быть вам подойдёт другая дата или другой город?"

        return "\n".join((p1, p2))

    @classmethod
    def missing_keys(cls, keys):
        p1 = "Для того, чтобы я смог выполнить поиск, мне необходимо знать следующую информацию:"
        p2 = ", ".join(cls.KEYS[key] for key in keys)

        return "\n".join((p1, p2))

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
