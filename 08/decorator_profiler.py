import cProfile
import io
import pstats
from functools import wraps


def profile_deco(func):
    profiler = cProfile.Profile()
    call_count = 0

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        profiler.enable()
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
        return result

    def print_stat():
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats(pstats.SortKey.CUMULATIVE)

        print(f"\n{'=' * 40}")
        print(f"Профилирование для функции {func.__name__} (всего вызовов: {call_count})")
        print('=' * 40)
        stats.print_stats()
        print(stream.getvalue())

    wrapper.print_stat = print_stat
    return wrapper


@profile_deco
def add(a, b):
    for _ in range(100_000):
        pass
    return a + b


@profile_deco
def sub(a, b):
    _ = list(range(100_000))
    return a - b


add(1, 2)
add(4, 5)
sub(4, 5)
sub(10, 3)
sub(7, 2)

add.print_stat()
sub.print_stat()
