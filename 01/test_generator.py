import pytest
from generator import check_line, search_in_file


@pytest.mark.parametrize(
    "line, search_words, stop_words, expected",
    [
        ("", ["фильтр"], ["стоп"], []),
        ("  ", ["фильтр"], ["стоп"], []),
        (None, ["фильтр"], ["стоп"], []),
        ("Строка с фильтр", ["фильтр"], ["стоп"], ["Строка с фильтр"]),
        ("Строка со Стоп", ["фильтр"], ["стоп"], []),
        ("Строка с фильтр и Стоп", ["фильтр"], ["стоп"], []),
        ("  Строка с фильтр  ", ["фильтр"], ["стоп"], ["Строка с фильтр"]),
        ("Строка с ФиЛЬтр", ["фильтр"], ["стоп"], ["Строка с ФиЛЬтр"]),
        ("Строка с фильтр фильтр", ["фильтр"], ["стоп"], ["Строка с фильтр фильтр"]),
        ("фильтр", ["фильтр"], ["стоп"], ["фильтр"]),
        ("стоп", ["фильтр"], ["стоп"], []),
        ("Строка с ф", ["ф"], ["стоп"], ["Строка с ф"]),
        ("Строка с оченьдлиннымфильтром", ["оченьдлиннымфильтром"], ["стоп"], ["Строка с оченьдлиннымфильтром"]),
        ("Строка со стоп", ["фильтр"], ["Стоп"], []),
    ],
)
def test_check_line(line, search_words, stop_words, expected):
    result = list(check_line(line, search_words, stop_words))
    assert result == expected


def test_search_in_file_basic(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с фильтр\nСтрока со Стоп\nДругая строка", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], ["стоп"]))
    assert result == ["Строка с фильтр"]


def test_search_in_file_not_found():
    with pytest.raises(FileNotFoundError):
        list(search_in_file("nonexistent_file.txt", ["фильтр"], ["стоп"]))


def test_search_in_file_multiple_filters(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с фильтр1 и фильтр2\nДругая строка", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр1", "фильтр2"], ["стоп"]))
    assert result == ["Строка с фильтр1 и фильтр2"]


def test_search_in_file_stop_word_takes_precedence(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с фильтр и стоп\nДругая строка", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], ["стоп"]))
    assert not result


def test_search_in_file_case_insensitive(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с ФиЛЬтр\nДругая строка", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], ["стоп"]))
    assert result == ["Строка с ФиЛЬтр"]


def test_search_in_file_single_character_filter(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с ф\nДругая строка", encoding='utf-8')
    result = list(search_in_file(str(p), ["ф"], ["стоп"]))
    assert result == ["Строка с ф"]


def test_search_in_file_empty_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], ["стоп"]))
    assert not result


def test_search_in_file_file_like_object(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с фильтр\nДругая строка", encoding='utf-8')
    with open(str(p), mode='r', encoding='utf-8') as file:
        result = list(search_in_file(file, ["фильтр"], ["стоп"]))
    assert result == ["Строка с фильтр"]


def test_search_in_file_long_line(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    long_line = "фильтр " * 1000 + "\n"
    p.write_text(long_line, encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], ["стоп"]))
    assert len(result) == 1
    assert result[0].startswith("фильтр")


def test_search_in_file_unicode_chars(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с üöäß Фильтр", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], ["стоп"]))
    assert result == ["Строка с üöäß Фильтр"]


def test_search_in_file_empty_search_words(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка без ничего", encoding='utf-8')
    result = list(search_in_file(str(p), [], ["стоп"]))
    assert not result


def test_search_in_file_empty_stop_words(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("Строка с фильтр", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], []))
    assert result == ["Строка с фильтр"]


def test_search_in_file_line_with_many_stop_words(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test_file.txt"
    p.write_text("строка стоп1 стоп2 стоп3 фильтр", encoding='utf-8')
    result = list(search_in_file(str(p), ["фильтр"], ["стоп1", "стоп2", "стоп3"]))
    assert not result
