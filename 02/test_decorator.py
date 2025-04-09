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
    assert "Функция func (попытка 1/3) выбросила исключение" in output
    assert "Повторная попытка через 1 секунду..." in output
    assert "Функция func (попытка 2/3) выполнена успешно" in output
    assert "Результат: 2" in output


def test_retry_deco_expected_error_immediately_raises():

    @retry_deco(retries=3, expected_errors=[ValueError])
    def func():
        raise ValueError("Expected error")

    with pytest.raises(ValueError, match="Expected error"):
        _, output = capture_output(func)

        assert "Функция func (попытка 1/3) выбросила исключение" in output
        assert "Исключение ValueError входит в список ожидаемых" in output
        assert "Повторная попытка" not in output


def test_retry_deco_all_retries_exhausted():

    @retry_deco(retries=2)
    def func():
        raise RuntimeError("Permanent error")

    with pytest.raises(RuntimeError, match="Permanent error"):
        _, output = capture_output(func)

        assert "Функция func (попытка 1/2) выбросила исключение" in output
        assert "Функция func (попытка 2/2) выбросила исключение" in output
        assert "Функция func не выполнена после 2 попыток" in output


def test_retry_deco_success_first_try():

    @retry_deco(retries=3)
    def func(x, y=0):
        return x * y

    result, output = capture_output(func, 3, y=2)

    assert result == 6
    assert "Функция func (попытка 1/3) выполнена успешно" in output
    assert "Результат: 6" in output
    assert "выбросила исключение" not in output


def test_retry_deco_sleep_between_retries():
    attempts = []

    with patch('time.sleep') as mock_sleep:
        @retry_deco(retries=3)
        def func():
            attempts.append(1)
            if len(attempts) < 3:
                raise RuntimeError("Error")
            return 42

        result = func()

        assert result == 42
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(1)
        assert len(attempts) == 3


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

        assert "KeyError: Unexpected error" in output
        assert "Повторная попытка через 1 секунду..." in output


def test_retry_deco_with_args_kwargs():

    @retry_deco()
    def func(a, b, *, c, d):
        return a + b + c + d

    result = func(1, 2, c=3, d=4)
    assert result == 10


@patch('time.sleep')
def test_retry_deco_sleep_called_once(mock_sleep):
    attempts = []

    @retry_deco(retries=2)
    def func():
        attempts.append(1)
        if len(attempts) < 2:
            raise Exception("Error")
        return "success"

    func()
    mock_sleep.assert_called_once_with(1)
