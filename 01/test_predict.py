from predict import predict_message_mood


def test_predict_positive_message():
    assert predict_message_mood("Чапаев и пустота") == "отл"


def test_predict_negative_message():
    assert predict_message_mood("Вулкан") == "неуд"


def test_predict_default_message():
    assert predict_message_mood("Some other message") == "норм"


def test_predict_at_bad_threshold():
    assert predict_message_mood("Some other message", bad_thresholds=0.5) == "норм"


def test_predict_at_good_threshold():
    assert predict_message_mood("Some other message", good_thresholds=0.5) == "норм"


def test_predict_custom_thresholds_1():
    assert predict_message_mood("Some other message", bad_thresholds=0.6, good_thresholds=0.7) == "неуд"


def test_predict_custom_thresholds_2():
    assert predict_message_mood("Some other message", bad_thresholds=0.1, good_thresholds=0.4) == "отл"


def test_predict_custom_thresholds_3():
    assert predict_message_mood("Some other message", bad_thresholds=0.1, good_thresholds=0.9) == "норм"


def test_predict_model_return_value():
    assert predict_message_mood("Чапаев и пустота", bad_thresholds=0.8, good_thresholds=0.99) == "норм"


def test_predict_empty_string():
    assert predict_message_mood("") == "норм"


def test_predict_unicode():
    assert predict_message_mood("Какое-то позитивное сообщение") == "норм"
