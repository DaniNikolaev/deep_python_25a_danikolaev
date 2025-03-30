from unittest.mock import patch
import pytest
from decorator import retry_deco


def test_retry_deco_success_immediately():

    @retry_deco()
    def mock_func():
        return "success"

    result = mock_func()
    assert result == "success"


def test_retry_deco_success_after_retries():

    attempts = []

    @retry_deco(retries=3)
    def mock_func():
        attempts.append(1)
        if len(attempts) < 3:
            raise Exception("Error")
        return "success"

    result = mock_func()
    assert result == "success"
    assert len(attempts) == 3


def test_retry_deco_failure_after_all_retries():

    @retry_deco(retries=2)
    def mock_func():
        raise Exception("Persistent Error")

    with pytest.raises(Exception, match="Persistent Error"):
        mock_func()


def test_retry_deco_with_expected_errors():

    @retry_deco(expected_errors=[ValueError])
    def mock_func():
        raise ValueError("Expected error")

    with pytest.raises(ValueError, match="Expected error"):
        mock_func()


def test_retry_deco_with_unexpected_errors():

    @retry_deco(expected_errors=[ValueError], retries=3)
    def mock_func():
        raise KeyError("Unexpected error")

    with pytest.raises(KeyError, match="Unexpected error"):
        mock_func()


def test_retry_deco_preserves_function_metadata():

    @retry_deco()
    def sample_func():
        """Sample docstring"""

    assert sample_func.__name__ == "sample_func"
    assert sample_func.__doc__ == "Sample docstring"


@patch('time.sleep')
def test_retry_deco_sleep_called(mock_sleep):
    attempts = []

    @retry_deco(retries=2)
    def mock_func():
        attempts.append(1)
        if len(attempts) < 2:
            raise Exception("Error")
        return "success"

    mock_func()
    mock_sleep.assert_called_once_with(1)


def test_retry_deco_with_args_kwargs():

    @retry_deco()
    def mock_func(a, b, *, c, d):
        return a + b + c + d

    result = mock_func(1, 2, c=3, d=4)
    assert result == 10
