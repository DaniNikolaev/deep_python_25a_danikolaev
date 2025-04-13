from functools import wraps
import time


def retry_deco(retries=3, expected_errors=None):
    if expected_errors is None:
        expected_errors = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None
            while attempt < retries:
                attempt += 1
                try:
                    result = func(*args, **kwargs)
                    print(f"Функция {func.__name__} (попытка {attempt}/{retries}) выполнена успешно. "
                          f"Аргументы: args={args}, kwargs={kwargs}. Результат: {result}")
                    return result
                except Exception as e:  # pylint: disable=broad-except
                    if any(isinstance(e, err_type) for err_type in expected_errors):
                        print(f"Функция {func.__name__} (попытка {attempt}/{retries}) выбросила ожидаемое исключение: "
                              f"{type(e).__name__}: {e}. Аргументы: args={args}, kwargs={kwargs}")
                        print(f"Исключение {type(e).__name__} входит в список ожидаемых. Выход из retry.")
                        raise
                    last_exception = e
                    print(f"Функция {func.__name__} (попытка {attempt}/{retries}) выбросила исключение: "
                          f"{type(e).__name__}: {e}. Аргументы: args={args}, kwargs={kwargs}")
                    if attempt < retries:
                        print("Повторная попытка через 1 секунду...")
                        time.sleep(1)
                    else:
                        print(f"Функция {func.__name__} не выполнена после {retries} попыток. "
                              f"Аргументы: args={args}, kwargs={kwargs}")
                        raise last_exception from last_exception

            print(f"Функция {func.__name__} не выполнена после {retries} попыток. "
                  f"Аргументы: args={args}, kwargs={kwargs}")
            raise last_exception from last_exception

        return wrapper
    return decorator
