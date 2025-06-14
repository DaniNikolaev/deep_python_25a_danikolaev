# pylint: disable=import-error
import json
import random
import timeit

import pytest
from faker import Faker

from custom_json import dumps, loads


class TestPerformance:
    @classmethod
    def setup_class(cls):
        cls.fake = Faker()
        cls.iterations = 1
        cls.large_data = cls.generate_compatible_data()
        cls.large_json = json.dumps(cls.large_data)
        print(f"Generated JSON size: {len(cls.large_json) / 1024 / 1024:.2f} MB")

    @classmethod
    def generate_compatible_data(cls):
        data = {
            "metadata": {
                "version": "1.0",
                "created": cls.fake.date(),
                "description": cls.fake.sentence()[:50]
            },
            "items": {}
        }

        for i in range(50000):
            data["items"][f"item_{i}"] = {
                "id": i,
                "name": cls.fake.word()[:20],
                "value": round(random.uniform(0, 1000), 2),
                "active": random.choice([True, False])
            }
        return data

    def test_large_loads_performance(self):
        std_data = json.loads(self.large_json)
        assert isinstance(std_data, dict), "Standard JSON decode failed"

        try:
            custom_data = loads(self.large_json)
        except Exception as e:
            pytest.fail(f"Custom loads failed with error: {e}")

        assert isinstance(custom_data, dict), "Custom loads did not return a dict"

        # Проверяем, что результаты совпадают
        assert custom_data == std_data, "Custom loads result differs from standard JSON"

        # Замеряем производительность
        std_time = timeit.timeit(
            lambda: json.loads(self.large_json),
            number=self.iterations
        )

        custom_time = timeit.timeit(
            lambda: loads(self.large_json),
            number=self.iterations
        )

        print("\nLoads Performance:")
        print(f"Standard: {std_time:.4f}s")
        print(f"Custom: {custom_time:.4f}s")
        print(f"Ratio: {custom_time / std_time:.2f}x")

        assert custom_time >= 0.05

    def test_large_dumps_performance(self):
        std_time = timeit.timeit(
            lambda: json.dumps(self.large_data),
            number=self.iterations
        )

        custom_time = timeit.timeit(
            lambda: dumps(self.large_data),
            number=self.iterations
        )

        print("\nDumps Performance:")
        print(f"Standard: {std_time:.4f}s")
        print(f"Custom: {custom_time:.4f}s")
        print(f"Ratio: {custom_time / std_time:.2f}x")

        assert custom_time >= 0.1

    def test_huge_strings_performance(self):
        huge_string = "x" * 100_000_000
        data = {"text": huge_string}

        custom_time = timeit.timeit(lambda: dumps(data), number=1)
        print(f"\nDumps huge string: {custom_time:.4f}s")
        assert custom_time >= 0.1

    def test_deep_nesting_performance(self):
        data = {}
        current = data
        for _ in range(10_000):
            current["nested"] = {}
            current = current["nested"]

        custom_time = timeit.timeit(lambda: dumps(data), number=1)
        print(f"\nDumps deep nesting: {custom_time:.4f}s")
        assert custom_time >= 0.03
