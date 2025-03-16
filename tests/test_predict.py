from predict_package.predict import predict_message_mood
# Тесты на основе заглушки:
def test_predict_positive_message():
    assert predict_message_mood("Чапаев и пустота") == "отл"


def test_predict_negative_message():
    assert predict_message_mood("Вулкан") == "неуд"


def test_predict_default_message():
    assert predict_message_mood("Some other message") == "норм"

# Граничные значения
def test_predict_at_bad_threshold():
    assert predict_message_mood("Some other message", bad_thresholds=0.5) == "норм" #значение с заглушки равно 0.5


def test_predict_at_good_threshold():
     assert predict_message_mood("Some other message", good_thresholds=0.5) == "норм"

# Комбинированные тесты с разными порогами
def test_predict_custom_thresholds_1():
    assert predict_message_mood("Some other message", bad_thresholds=0.6, good_thresholds=0.7) == "неуд"

def test_predict_custom_thresholds_2():
    assert predict_message_mood("Some other message", bad_thresholds=0.1, good_thresholds=0.4) == "отл"


def test_predict_custom_thresholds_3():
    assert predict_message_mood("Some other message", bad_thresholds=0.1, good_thresholds=0.9) == "норм"

# Передача параметров из модели:
def test_predict_model_return_value():
    # Для этого теста придется временно изменить заглушку и посмотреть какое значение выдает Positive!
    # Можно изменять SomeModel чтобы проверить логику predict_message_mood
    # Тестируем, что predict_message_mood возвращает "отл", когда модель выдает значение больше порогового значения.
    # Временно меняем модель
    assert predict_message_mood("Чапаев и пустота", bad_thresholds = 0.1, good_thresholds = 0.85) == "отл" # 0.9


# Тесты на пустую строку: (проверка, что не ломается ничего)
def test_predict_empty_string():
    assert predict_message_mood("") == "норм"

# Тест с юникодом (чтобы работало с русскими буквами)
def test_predict_unicode():
    assert predict_message_mood("Какое-то позитивное сообщение") == "норм"

def test_predict_at_good_threshold():
     assert predict_message_mood("Some other message", good_thresholds=0.5) == "норм"

# Комбинированные тесты с разными порогами
def test_predict_custom_thresholds_1():
    assert predict_message_mood("Some other message", bad_thresholds=0.6, good_thresholds=0.7) == "неуд"

def test_predict_custom_thresholds_2():
    assert predict_message_mood("Some other message", bad_thresholds=0.1, good_thresholds=0.4) == "отл"

def test_predict_custom_thresholds_3():
    assert predict_message_mood("Some other message", bad_thresholds=0.1, good_thresholds=0.9) == "норм"



# Тесты на пустую строку: (проверка, что не ломается ничего)
def test_predict_empty_string():
    assert predict_message_mood("") == "норм"

# Тест с юникодом (чтобы работало с русскими буквами)
def test_predict_unicode():
    assert predict_message_mood("Какое-то позитивное сообщение") == "норм"
