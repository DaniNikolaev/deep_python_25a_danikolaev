import hashlib


class SomeModel:
    def predict(self, message: str) -> float:
        # Реализация не важна.  В данном случае сделаем заглушку, возвращающую разные значения для разных сообщений
        if message == "Чапаев и пустота":
            return 0.9  # Чтобы проходил первый assert
        elif message == "Вулкан":
            return 0.2  # Чтобы проходил третий assert
        else:
            return 0.5  # Значение по умолчанию, чтобы проходил assert, если ни один из if не сработал


def predict_message_mood(
    message: str,
    bad_thresholds: float = 0.3,
    good_thresholds: float = 0.8,
) -> str:
    model = SomeModel()
    value = model.predict(message)
    if value < bad_thresholds:
        return 'неуд'
    if value > good_thresholds:
        return 'отл'
    return 'норм'



# assert predict_message_mood("Чапаев и пустота") == "отл"
# assert predict_message_mood("Чапаев и пустота", 0.8, 0.99) == "норм"
# assert predict_message_mood("Вулкан") == "неуд"

