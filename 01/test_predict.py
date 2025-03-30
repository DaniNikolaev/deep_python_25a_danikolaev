# pylint: disable=E1101
import pytest
from predict import SomeModel, predict_message_mood


@pytest.mark.parametrize(
    "message, return_value, expected_result",
    [
        ("positive message", 0.9, "отл"),
        ("negative message", 0.2, "неуд"),
        ("neutral message", 0.5, "норм"),

        ("just below bad", 0.299, "неуд"),
        ("just above bad", 0.301, "норм"),
        ("exactly bad threshold", 0.3, "норм"),
        ("exactly good threshold", 0.8, "норм"),
        ("just below good", 0.799, "норм"),
        ("just above good", 0.801, "отл"),

        # Разные типы сообщений
        ("", 0.5, "норм"),
        ("   ", 0.5, "норм"),
        ("Very long message with many words and characters...", 0.5, "норм"),
        ("Symbols!@#$%^&*()_+=-`~", 0.5, "норм"),
        ("Mixed case Message", 0.5, "норм"),
        ("юникод 文字列", 0.5, "норм"),

        pytest.param("custom threshold test", 0.4, "неуд", marks=pytest.mark.custom_thresholds),
        pytest.param("custom threshold test", 0.5, "норм", marks=pytest.mark.custom_thresholds),
        pytest.param("custom threshold test", 0.6, "норм", marks=pytest.mark.custom_thresholds),
        pytest.param("custom threshold test", 0.7, "норм", marks=pytest.mark.custom_thresholds),
        pytest.param("custom threshold test", 0.799, "отл", marks=pytest.mark.custom_thresholds)
    ],
)
def test_predict_message_mood(mocker, message, return_value, expected_result):
    mocker.patch.object(SomeModel, 'predict', return_value=return_value)
    if "custom threshold test" in message:
        result = predict_message_mood(message, bad_thresholds=0.5, good_thresholds=0.7)
    else:
        result = predict_message_mood(message)
    assert result == expected_result
    SomeModel.predict.assert_called_once_with(message)
