from unittest.mock import patch
import pytest
from custom_list import CustomList


class TestCustomList:

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], 2, [3, 4, 5]),
            ([1, 2, 3], [4, 5, 6], [5, 7, 9]),
            ([1, 2, 3], CustomList([4, 5, 6]), [5, 7, 9]),
            ([1, 2, 3], [4, 5], [5, 7, 3]),
            ([1, 2], [4, 5, 6], [5, 7, 6]),
            ([1, 2, 3], [], [1, 2, 3]),
            ([], [1, 2, 3], [1, 2, 3]),
        ],
    )
    def test_add(self, list1, list2, expected):
        cl1 = CustomList(list1)
        result = cl1 + list2
        assert result == CustomList(expected)

    def test_add_invalid_type(self):
        cl = CustomList([1, 2, 3])
        result = cl + "string"
        assert result is None

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], 2, [3, 4, 5]),
            ([1, 2, 3], [4, 5, 6], [5, 7, 9]),
            ([1, 2, 3], CustomList([4, 5, 6]), [5, 7, 9]),
            ([1, 2, 3], [4, 5], [5, 7, 3]),
            ([1, 2], [4, 5, 6], [5, 7, 6]),
            ([1, 2, 3], [], [1, 2, 3]),
            ([], [1, 2, 3], [1, 2, 3]),
        ],
    )
    def test_radd(self, list1, list2, expected):
        cl1 = CustomList(list1)
        result = list2 + cl1
        assert result == CustomList(expected)

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], 2, [-1, 0, 1]),
            ([1, 2, 3], [4, 5, 6], [-3, -3, -3]),
            ([1, 2, 3], CustomList([4, 5, 6]), [-3, -3, -3]),
            ([1, 2, 3], [4, 5], [-3, -3, 3]),
            ([1, 2], [4, 5, 6], [-3, -3, -6]),
            ([1, 2, 3], [], [1, 2, 3]),
            ([], [1, 2, 3], [-1, -2, -3]),
        ],
    )
    def test_sub(self, list1, list2, expected):
        cl1 = CustomList(list1)
        result = cl1 - list2
        assert result == CustomList(expected)

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], 2, [1, 0, -1]),
            ([1, 2, 3], [4, 5, 6], [3, 3, 3]),
            ([1, 2, 3], CustomList([4, 5, 6]), [3, 3, 3]),
            ([1, 2, 3], [4, 5], [3, 3, -3]),
            ([1, 2], [4, 5, 6], [3, 3, 6]),
            ([1, 2, 3], [], [-1, -2, -3]),
            ([], [1, 2, 3], [1, 2, 3]),
        ],
    )
    def test_rsub(self, list1, list2, expected):
        cl1 = CustomList(list1)
        result = list2 - cl1
        assert result == CustomList(expected)

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [3, 2, 1], True),
            ([1, 2, 3], [1, 2, 4], False),
        ],
    )
    def test_eq(self, list1, list2, expected):
        cl1 = CustomList(list1)
        cl2 = CustomList(list2)
        assert (cl1 == cl2) == expected

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [1, 2, 4], True),
            ([1, 2, 3], [1, 2, 2], False),
            ([1, 2, 3], [1, 2, 3], False),
        ],
    )
    def test_lt(self, list1, list2, expected):
        cl1 = CustomList(list1)
        cl2 = CustomList(list2)
        assert (cl1 < cl2) == expected

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [1, 2, 4], True),
            ([1, 2, 3], [1, 2, 3], True),
            ([1, 2, 3], [1, 2, 2], False),
        ],
    )
    def test_le(self, list1, list2, expected):
        cl1 = CustomList(list1)
        cl2 = CustomList(list2)
        assert (cl1 <= cl2) == expected

    def test_str(self):
        cl = CustomList([1, 2, 3])
        assert str(cl) == "1 2 3 Сумма: 6"

    def test_add_extend_side_effect(self):
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        cl_copy = cl.copy()
        other_copy = other.copy()

        with patch.object(CustomList, '_CustomList__calculate') as mock_calculate:
            cl + other
            if len(cl_copy) < len(other_copy):
                assert mock_calculate.call_count > 0
            else:
                assert mock_calculate.call_count > 0

            assert cl == cl_copy
            assert other == other_copy

    def test_sub_extend_side_effect(self):
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        cl_copy = cl.copy()
        other_copy = other.copy()

        with patch.object(CustomList, '_CustomList__calculate') as mock_calculate:
            cl - other
            if len(cl_copy) < len(other_copy):
                assert mock_calculate.call_count > 0
            else:
                assert mock_calculate.call_count > 0

            assert cl == cl_copy
            assert other == other_copy

    def test_rsub_extend_side_effect(self):
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        cl_copy = cl.copy()
        other_copy = other.copy()

        with patch.object(CustomList, '_CustomList__calculate') as mock_calculate:
            other - cl
            if len(cl_copy) > len(other_copy):
                assert mock_calculate.call_count > 0
            else:
                assert mock_calculate.call_count > 0

            assert cl == cl_copy
            assert other == other_copy
