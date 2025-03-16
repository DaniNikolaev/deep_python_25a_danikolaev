

class SomeModel:
    def predict(self, message: str) -> float:
        if message == "Чапаев и пустота":
            return 0.9
        if message == "Вулкан":
            return 0.2
        return 0.5


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
