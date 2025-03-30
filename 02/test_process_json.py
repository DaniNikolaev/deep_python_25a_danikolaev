import pytest
from process_json import check_token_in_values, create_dict_from_str, process_json  # Замените your_module


@pytest.mark.parametrize(
    "token, values, expected",
    [
        ("token", ["token"], True),
        ("Token", ["token"], True),
        ("token", ["Token"], True),
        ("tOkEn", ["ToKeN"], True),
        ("token", ["not_token"], False),
        ("token", [], False),
        ("token", ["token", "another_token"], True),
        ("token", ["another_token", "token"], True),
        ("token", ["token token"], False),
        ("token", ["prefix_token", "token_suffix"], False),
        ("token", ["token", "Token", "TOKEN"], True)
    ],
)
def test_check_token_in_values(token, values, expected):
    assert check_token_in_values(token, values) == expected


def test_create_dict_from_str_valid_json():
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    expected = {"key1": ["value1", "value2"], "key2": ["value3"]}
    assert create_dict_from_str(json_str) == expected


def test_create_dict_from_str_empty_json():
    json_str = '{}'
    assert not create_dict_from_str(json_str)


def test_create_dict_from_str_json_with_numbers():
    json_str = '{"key1": "123 456", "key2": "abc"}'
    expected = {"key1": ["123", "456"], "key2": ["abc"]}
    assert create_dict_from_str(json_str) == expected


def test_create_dict_from_str_json_with_special_chars():
    json_str = '{"key1": "value!@# value$%", "key2": "value^&*"}'
    expected = {"key1": ["value!@#", "value$%"], "key2": ["value^&*"]}
    assert create_dict_from_str(json_str) == expected


def test_create_dict_from_str_invalid_json_format():
    json_str = 'invalid json'
    with pytest.raises(ValueError):
        create_dict_from_str(json_str)


def test_create_dict_from_str_json_not_a_dict():
    json_str = '["value1", "value2"]'
    with pytest.raises(ValueError):
        create_dict_from_str(json_str)


def test_create_dict_from_str_json_values_not_string():
    json_str = '{"key1": 123, "key2": "value"}'
    with pytest.raises(ValueError):
        create_dict_from_str(json_str)


def test_create_dict_from_str_empty_string_values():
    json_str = '{"key1": ""}'
    expected = {"key1": []}
    assert create_dict_from_str(json_str) == expected


def test_create_dict_from_str_json_with_unicode():
    json_str = '{"key1": "значение1 значение2", "key2": "value3"}'
    expected = {"key1": ["значение1", "значение2"], "key2": ["value3"]}
    assert create_dict_from_str(json_str) == expected


def test_process_json_basic(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    required_keys = ["key1"]
    tokens = ["value1"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == "key1: value1\n"


def test_process_json_no_matching_keys(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    required_keys = ["key3"]
    tokens = ["value1"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_process_json_no_matching_tokens(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    required_keys = ["key1"]
    tokens = ["value4"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_process_json_case_insensitive_token_matching(capsys):
    json_str = '{"key1": "Value1 value2", "key2": "value3"}'
    required_keys = ["key1"]
    tokens = ["value1"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == "key1: value1\n"


def test_process_json_case_sensitive_key_matching(capsys):
    json_str = '{"Key1": "value1 value2", "key2": "value3"}'
    required_keys = ["Key1"]
    tokens = ["value1"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == "Key1: value1\n"


def test_process_json_empty_required_keys(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    required_keys = []
    tokens = ["value1"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_process_json_empty_tokens(capsys):
    json_str = '{"key1": "value1 value2", "key2": "value3"}'
    required_keys = ["key1"]
    tokens = []

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_process_json_no_callback(capsys):
    json_str = '{"key1": "value1 value2"}'
    required_keys = ["key1"]
    tokens = ["value1"]

    process_json(json_str, required_keys, tokens)
    captured = capsys.readouterr()
    assert "key1: value1" in captured.out


def test_process_json_invalid_json_string(capsys):
    json_str = 'invalid json'
    required_keys = ["key1"]
    tokens = ["value1"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert "Ошибка" in captured.out


def test_process_json_value_is_not_string(capsys):
    json_str = '{"key1": 123}'
    required_keys = ["key1"]
    tokens = ["123"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert "Ошибка" in captured.out


def test_process_json_value_with_special_characters(capsys):
    json_str = '{"key1": "value!@#value$%"}'
    required_keys = ["key1"]
    tokens = ["value!@#value$%"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == "key1: value!@#value$%\n"


def test_process_json_multiple_tokens_in_value(capsys):
    json_str = '{"key1": "value1 value1"}'
    required_keys = ["key1"]
    tokens = ["value1"]

    def callback(key, token):
        return f"{key}: {token}"

    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == "key1: value1\n"


def test_process_json_empty_values(capsys):
    json_str = '{"key1": ""}'
    required_keys = ["key1"]
    tokens = ["any"]

    def callback(key, token):
        return f"{key}: {token}"
    process_json(json_str, required_keys, tokens, callback)
    captured = capsys.readouterr()
    assert captured.out == ""
