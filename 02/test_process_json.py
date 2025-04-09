from unittest.mock import Mock
import pytest
from process_json import check_token_in_values, create_dict_from_str, process_json


def test_check_token_in_values():
    assert check_token_in_values("test", ["test", "value"]) is True
    assert check_token_in_values("TEST", ["test", "value"]) is True
    assert check_token_in_values("test", ["value1", "value2"]) is False
    assert check_token_in_values("test", []) is False


def test_create_dict_from_str_valid():
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    result = create_dict_from_str(json_str)
    assert result == {"key1": ["value1", "value2"], "key2": ["value3"]}


def test_create_dict_from_str_invalid_json():
    with pytest.raises(ValueError, match="Ошибка декодирования JSON"):
        create_dict_from_str("{invalid}")


def test_create_dict_from_str_not_dict():
    with pytest.raises(ValueError, match="Строка должна представлять JSON-словарь"):
        create_dict_from_str('["not", "a", "dict"]')


def test_create_dict_from_str_non_string_values():
    with pytest.raises(ValueError, match="Значения в JSON должны быть строками"):
        create_dict_from_str('{"key": 123}')


def test_process_json_basic(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    process_json(json_str, required_keys=["key1"], tokens=["value1"])
    captured = capsys.readouterr()
    assert captured.out.strip() == "key1: value1"


def test_process_json_multiple_tokens_same_key(capsys):
    """Тест с несколькими токенами для одного ключа - вывод должен быть в отдельных строках"""
    json_str = '{"key1": "value1 value2 value3", "key2": "value4"}'
    process_json(json_str, required_keys=["key1"], tokens=["value1", "value3"])
    captured = capsys.readouterr()
    lines = captured.out.strip().split('\n')
    assert len(lines) == 2
    assert "key1: value1" in lines[0]
    assert "key1: value3" in lines[1]
    assert captured.out.count("key1:") == 2


def test_process_json_multiple_keys_tokens(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value3 value4", "key3": "value5"}'
    process_json(json_str, required_keys=["key1", "key2"], tokens=["value1", "value4"])
    captured = capsys.readouterr()
    assert "key1: value1" in captured.out
    assert "key2: value4" in captured.out
    assert "key3" not in captured.out


def test_process_json_case_insensitive(capsys):
    """Тест регистронезависимости с правильными ключами"""
    json_str = '{"KEY1": "VALUE1 value2", "key2": "value3"}'
    process_json(json_str, required_keys=["KEY1"], tokens=["value1"])
    captured = capsys.readouterr()
    assert "KEY1: value1" in captured.out


def test_process_json_callback(capsys):
    json_str = '{"key1": "value1 value2"}'
    mock_callback = Mock(return_value="callback_output")
    process_json(json_str, required_keys=["key1"], tokens=["value1"], callback=mock_callback)

    mock_callback.assert_called_once_with("key1", "value1")

    captured = capsys.readouterr()
    assert "callback_output" in captured.out


def test_process_json_invalid_json(capsys):
    process_json("{invalid}", required_keys=["key1"], tokens=["value1"])
    captured = capsys.readouterr()
    assert "Ошибка: Ошибка декодирования JSON" in captured.out


def test_process_json_no_matches(capsys):
    json_str = '{"key1": "value1", "key2": "value2"}'
    process_json(json_str, required_keys=["key3"], tokens=["value1"])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_process_json_empty_input(capsys):
    process_json("{}", required_keys=[], tokens=[])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_process_json_token_in_multiple_values(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value1 value3"}'
    process_json(json_str, required_keys=["key1", "key2"], tokens=["value1"])
    captured = capsys.readouterr()
    assert "key1: value1" in captured.out
    assert "key2: value1" in captured.out
    assert captured.out.count("value1") == 2


def test_process_json_empty_tokens(capsys):
    json_str = '{"key1": "value1"}'
    process_json(json_str, required_keys=["key1"], tokens=[])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_process_json_empty_required_keys(capsys):
    json_str = '{"key1": "value1"}'
    process_json(json_str, required_keys=[], tokens=["value1"])
    captured = capsys.readouterr()
    assert captured.out == ""
