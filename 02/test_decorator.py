from io import StringIO
import sys
from unittest.mock import patch
import pytest
from decorator import retry_deco


def capture_output(func, *args, **kwargs):
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        result = func(*args, **kwargs)
        output = sys.stdout.getvalue()
        return result, output
    except Exception as e:
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        raise e
    finally:
        sys.stdout = old_stdout


def test_retry_deco_success_after_retry():
    attempts = []

    @retry_deco(retries=3)
    def func(x):
        attempts.append(1)
        if len(attempts) < 2:
            raise RuntimeError("Temporary error")
        return x * 2

    result, output = capture_output(func, 1)

    assert result == 2
    assert len(attempts) == 2
    expected_output = [
        "Функция func (попытка 1/3) выбросила исключение: RuntimeError: Temporary error. Аргументы: args=(1,), kwargs={}",
        "Повторная попытка через 1 секунду...",
        "Функция func (попытка 2/3) выполнена успешно. Аргументы: args=(1,), kwargs={}. Результат: 2"
    ]
    for line in expected_output:
        assert line in output
    assert output.count("попытка") == 3


def test_retry_deco_expected_error_immediately_raises():
    @retry_deco(retries=3, expected_errors=[ValueError])
    def func():
        raise ValueError("Expected error")

    with pytest.raises(ValueError, match="Expected error"):
        _, output = capture_output(func)

        expected_output = [
            "Функция func (попытка 1/3) выбросила ожидаемое исключение: ValueError: Expected error. Аргументы: args=(), kwargs={}",
            "Исключение ValueError входит в список ожидаемых. Выход из retry."
        ]
        for line in expected_output:
            assert line in output
        assert "Повторная попытка" not in output
        assert output.count("попытка") == 1


def test_retry_deco_all_retries_exhausted():
    @retry_deco(retries=2)
    def func():
        raise RuntimeError("Permanent error")

    with pytest.raises(RuntimeError, match="Permanent error"):
        _, output = capture_output(func)

        expected_output = [
            "Функция func (попытка 1/2) выбросила исключение: RuntimeError: Permanent error. Аргументы: args=(), kwargs={}",
            "Повторная попытка через 1 секунду...",
            "Функция func (попытка 2/2) выбросила исключение: RuntimeError: Permanent error. Аргументы: args=(), kwargs={}",
            "Функция func не выполнена после 2 попыток. Аргументы: args=(), kwargs={}"
        ]
        for line in expected_output:
            assert line in output
        assert output.count("Повторная попытка") == 1


def test_retry_deco_success_first_try():
    @retry_deco(retries=3)
    def func(x, y=0):
        return x * y

    result, output = capture_output(func, 3, y=2)

    assert result == 6
    expected_output = (
        "Функция func (попытка 1/3) выполнена успешно. "
        "Аргументы: args=(3,), kwargs={'y': 2}. Результат: 6"
    )
    assert expected_output in output
    assert "выбросила исключение" not in output
    assert output.count("попытка") == 1


def test_retry_deco_sleep_between_retries():
    attempts = []

    with patch('time.sleep') as mock_sleep:
        @retry_deco(retries=3)
        def func():
            attempts.append(1)
            if len(attempts) < 3:
                raise RuntimeError("Error")
            return 42

        result, output = capture_output(func)

        assert result == 42
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(1)
        assert len(attempts) == 3
        assert output.count("Повторная попытка через 1 секунду...") == 2


def test_retry_deco_preserves_metadata():
    @retry_deco()
    def original_func(x, y=0):
        """Test function"""
        return x * y

    assert original_func.__name__ == "original_func"
    assert original_func.__doc__ == "Test function"
    assert original_func.__module__ == __name__


def test_retry_deco_with_unexpected_errors():
    @retry_deco(expected_errors=[ValueError], retries=3)
    def func():
        raise KeyError("Unexpected error")

    with pytest.raises(KeyError, match="Unexpected error"):
        _, output = capture_output(func)

        expected_output = [
            "Функция func (попытка 1/3) выбросила исключение: KeyError: Unexpected error. Аргументы: args=(), kwargs={}",
            "Повторная попытка через 1 секунду...",
            "Функция func не выполнена после 3 попыток. Аргументы: args=(), kwargs={}"
        ]
        for line in expected_output:
            assert line in output
        assert output.count("Повторная попытка") == 3


def test_retry_deco_with_args_kwargs():
    @retry_deco()
    def func(a, b, *, c, d):
        return a + b + c + d

    result, output = capture_output(func, 1, 2, c=3, d=4)
    assert result == 10
    assert "Аргументы: args=(1, 2), kwargs={'c': 3, 'd': 4}" in output


@patch('time.sleep')
def test_retry_deco_sleep_called_once(mock_sleep):
    attempts = []

    @retry_deco(retries=2)
    def func():
        attempts.append(1)
        if len(attempts) < 2:
            raise Exception("Error")
        return "success"

    result, output = capture_output(func)
    assert result == "success"
    mock_sleep.assert_called_once_with(1)
    assert "Аргументы: args=(), kwargs={}" in output
    assert output.count("попытка") == 3


def test_retry_deco_no_retries_on_expected_error():
    @retry_deco(retries=5, expected_errors=[TypeError])
    def func(x):
        if x < 0:
            raise TypeError("Negative value")
        return x * 2

    with pytest.raises(TypeError, match="Negative value"):
        _, output = capture_output(func, -1)

        expected_output = [
            "Функция func (попытка 1/5) выбросила ожидаемое исключение: TypeError: Negative value. Аргументы: args=(-1,), kwargs={}",
            "Исключение TypeError входит в список ожидаемых. Выход из retry."
        ]
        for line in expected_output:
            assert line in output
        assert output.count("попытка") == 1

    result, output = capture_output(func, 2)
    assert result == 4
    assert "Аргументы: args=(2,), kwargs={}" in output
