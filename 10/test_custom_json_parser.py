import pytest

from custom_json import dumps, loads

TEST_CASES = [
    ('{"name": "Alice", "age": 25}', {"name": "Alice", "age": 25}),
    ('{"empty": {}}', {"empty": {}}),
    ('{"numbers": [1, 2, 3]}', {"numbers": [1, 2, 3]}),
]


@pytest.mark.parametrize("json_str,expected", TEST_CASES)
def test_loads(json_str, expected):
    if expected is None:
        with pytest.raises((TypeError, ValueError)):
            loads(json_str)
    else:
        assert loads(json_str) == expected


def test_dumps():
    data = {"name": "Bob", "age": 30}
    assert dumps(data) == '{"name": "Bob", "age": 30}'


def test_roundtrip():
    data = {"key": "value", "num": 42}
    assert loads(dumps(data)) == data


def test_basic_loads():
    simple_json = '{"key": "value"}'
    result = loads(simple_json)
    assert isinstance(result, dict)
    assert result["key"] == "value"


def test_basic_dumps():
    simple_dict = {"key": "value"}
    result = dumps(simple_dict)
    assert result == '{"key": "value"}'


def test_empty_dict():
    assert loads(dumps({})) == {}
