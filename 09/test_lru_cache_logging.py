# pylint: disable=redefined-outer-name
import logging
import os
import sys
from unittest.mock import patch

import pytest
from lru_cache_logging import EvenWordsFilter, LRUCache, main, setup_logging


def test_even_words_filter():
    ewf = EvenWordsFilter()
    assert ewf.filter(logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="Добавлен новый ключ 'a' со значением '1'", args=(), exc_info=None
    )) is True

    assert ewf.filter(logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="Ключ 'missing' не найден в кэше", args=(), exc_info=None
    )) is False


def test_filter_with_various_messages():
    ewf = EvenWordsFilter()

    test_cases = [
        ("", True),
        ("Один", False),
        ("Два слова", True),
        ("Три слова здесь", False),
        ("Ключ 'a' = 1", True)
    ]

    for msg, should_filter in test_cases:
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg=msg, args=(), exc_info=None
        )
        assert ewf.filter(record) == (not should_filter)


@pytest.fixture
def log_file():
    logging.shutdown()
    if os.path.exists('cache.log'):
        os.remove('cache.log')
    yield
    logging.shutdown()
    if os.path.exists('cache.log'):
        os.remove('cache.log')


def read_log_file():
    try:
        with open('cache.log', 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open('cache.log', 'r', encoding='cp1251') as f:
            return f.read()


def test_logging_to_file(log_file):
    setup_logging(use_stdout=False, use_filter=False)
    cache = LRUCache(limit=2)

    cache.set('a', 1)
    cache.get('a')
    cache.get('missing_key')

    logs = read_log_file()

    assert "Добавлен новый ключ 'a' со значением '1'" in logs
    assert "Полученный ключ 'a' со значением '1'" in logs
    assert "Ключ 'missing_key' не найден в кэше" in logs


def test_stdout_logging(capsys, log_file):
    setup_logging(use_stdout=True, use_filter=False)
    cache = LRUCache(limit=2)

    cache.set('x', 10)
    cache.get('x')

    captured = capsys.readouterr()
    output = captured.out

    assert "[INFO] Добавлен новый ключ 'x' со значением '10'" in output
    assert "[INFO] Полученный ключ 'x' со значением '10'" in output


def test_filter_logging(capsys, log_file):
    setup_logging(use_stdout=True, use_filter=True)
    cache = LRUCache(limit=2)

    cache.set('a', 1)

    cache.get('missing')

    captured = capsys.readouterr()
    output = captured.out

    assert "Добавлен новый ключ 'a' со значением '1'" in output

    assert "Ключ 'missing' не найден в кэше" not in output


def test_main_with_args(capsys, log_file):
    test_args = ["program", "-s", "-f"]
    with patch.object(sys, 'argv', test_args):
        main()

    captured = capsys.readouterr()
    output = captured.out

    assert any(
        msg in output
        for msg in [
            "Достигнут limit кэша",
            "Ключ 'x' не найден в кэше",
            "Удален node с ключом"
        ]
    )


def test_cache_state_logging(log_file):
    setup_logging(use_stdout=False, use_filter=False)
    cache = LRUCache(limit=2)

    cache.set('a', 1)
    cache.set('b', 2)

    logs = read_log_file()

    assert "Состояние кэша после add 'a':" in logs
    assert "Состояние кэша после add 'b':" in logs


def test_debug_logs(log_file):
    setup_logging(use_stdout=False, use_filter=False)
    cache = LRUCache(limit=2)

    cache.set('a', 1)
    cache.set('b', 2)
    cache.get('a')

    logs = read_log_file()

    assert "Добавлен первый node в кэш" in logs
    assert "Сдвинут node с ключом 'a' в голову кэша" in logs


def test_cache_overflow_logging(log_file):
    setup_logging(use_stdout=False, use_filter=False)
    cache = LRUCache(limit=2)

    cache.set('a', 1)
    cache.set('b', 2)
    cache.set('c', 3)

    logs = read_log_file()

    assert "Достигнут limit кэша" in logs
    assert "Удален node с ключом 'a'" in logs
    assert "Добавлен новый ключ 'c'" in logs


def test_key_update_logging(log_file):
    setup_logging(use_stdout=False, use_filter=False)
    cache = LRUCache(limit=2)

    cache.set('a', 1)
    cache.set('a', 2)

    logs = read_log_file()

    assert "Обновленный ключ 'a'" in logs
    assert "Состояние кэша после update 'a': a:2" in logs
