# pylint: disable=redefined-outer-name
import pytest
from generator import search_in_file, check_line

TEST_FILE_CONTENT = [
    "а Роза упала на лапу Азора",
    "Роза упала",
    "Упала роза на лапу",
    "розан упал",
    "Собака Азора спит",
    "кошка Мурка спит",
    ""
]

SEARCH_WORDS = ["роза", "кошка"]
STOP_WORDS = ["азора", "собака"]


@pytest.fixture
def temp_test_file(tmp_path):
    d = tmp_path / "test_data"
    d.mkdir()
    p = d / "test.txt"
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(TEST_FILE_CONTENT))
    return str(p)


@pytest.fixture
def lines_for_test():
    return TEST_FILE_CONTENT


def test_check_line_basic():
    result = list(check_line("Роза упала", SEARCH_WORDS, STOP_WORDS))
    assert result == ["Роза упала"]


def test_check_line_stop_word():
    result = list(check_line("Собака Азора спит", SEARCH_WORDS, STOP_WORDS))
    assert not result


def test_check_line_no_match():
    result = list(check_line("слон спит", SEARCH_WORDS, STOP_WORDS))
    assert not result


def test_check_line_empty_line():
    result = list(check_line("", SEARCH_WORDS, STOP_WORDS))
    assert not result


def test_search_in_file_basic(temp_test_file):
    expected_result = ["Роза упала", "Упала роза на лапу", "кошка Мурка спит"]
    result = list(search_in_file(temp_test_file, SEARCH_WORDS, STOP_WORDS))
    assert result == expected_result


def test_search_in_file_file_not_found():
    with pytest.raises(FileNotFoundError):
        list(search_in_file("nonexistent_file.txt", SEARCH_WORDS, STOP_WORDS))


def test_search_in_file_empty_file(temp_test_file):
    with open(temp_test_file, "w", encoding="utf-8") as f:
        f.write("")
    result = list(search_in_file(temp_test_file, SEARCH_WORDS, STOP_WORDS))
    assert not result


def test_search_in_file_with_file_object(temp_test_file):
    with open(temp_test_file, 'r', encoding='utf-8') as f:
        result = list(search_in_file(f, SEARCH_WORDS, STOP_WORDS))
    expected_result = ["Роза упала", "Упала роза на лапу", "кошка Мурка спит"]
    assert result == expected_result


def test_search_in_file_no_matches(temp_test_file):
    result = list(search_in_file(temp_test_file, ["слон"], ["тигр"]))
    assert not result


def test_search_in_file_only_stopwords(temp_test_file):
    result = list(search_in_file(temp_test_file, ["слон"], ["азора", "собака", "роза", "кошка"]))
    assert not result


def test_search_in_file_with_test_lines(lines_for_test):
    expected_result = ["Роза упала", "Упала роза на лапу", "кошка Мурка спит"]
    result = list(search_in_file(lines_for_test, SEARCH_WORDS, STOP_WORDS))
    assert result == expected_result
