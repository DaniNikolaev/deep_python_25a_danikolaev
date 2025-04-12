import pytest
from custom_list import CustomList


class TestCustomList:
    @staticmethod
    def check_original_unchanged(original1, original2, operation):
        original1_copy = original1.copy()
        original2_copy = original2.copy()\
            if hasattr(original2, 'copy') \
            else list(original2) if isinstance(original2, (list, CustomList)) else original2

        result = operation()

        assert list(original1) == list(original1_copy)
        if isinstance(original2, (list, CustomList)):
            assert list(original2) == list(original2_copy)
        else:
            assert original2 == original2_copy
        return result

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
        other = list2

        def operation():
            return cl1 + other

        result = self.check_original_unchanged(cl1, other, operation)

        assert isinstance(result, CustomList)
        assert list(result) == expected
        assert sum(result) == sum(expected)

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
        other = list2

        def operation():
            return other + cl1

        result = self.check_original_unchanged(cl1, other, operation)

        assert isinstance(result, CustomList)
        assert list(result) == expected
        assert sum(result) == sum(expected)

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
        other = list2

        def operation():
            return cl1 - other

        result = self.check_original_unchanged(cl1, other, operation)

        assert isinstance(result, CustomList)
        assert list(result) == expected
        assert sum(result) == sum(expected)

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
        other = list2

        def operation():
            return other - cl1

        result = self.check_original_unchanged(cl1, other, operation)

        assert isinstance(result, CustomList)
        assert list(result) == expected
        assert sum(result) == sum(expected)

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [1, 2, 3], True),
            ([1, 2, 3], [3, 2, 1], False),
            ([1, 2, 3], [1, 2, 4], False),
            ([1, 2, 3], [6], False),
            ([1, 2, 3], [1, 2], False),
            ([], [], True),
            ([1, 2, 3], CustomList([1, 2, 3]), True),
            ([1, 2, 3], [1, 2, 3], True),
        ],
    )
    def test_eq(self, list1, list2, expected):
        cl1 = CustomList(list1)
        if isinstance(list2, CustomList):
            cl2 = list2
        else:
            cl2 = CustomList(list2) if isinstance(list2, list) else list2

        assert (cl1 == cl2) == expected
        if isinstance(cl2, (CustomList, list)):
            assert (cl2 == cl1) == expected

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [1, 2, 3], False),
            ([1, 2, 3], [3, 2, 1], True),
            ([1, 2, 3], [1, 2, 4], True),
            ([1, 2, 3], [6], True),
            ([1, 2, 3], [1, 2], True),
            ([], [], False),
            ([1, 2, 3], CustomList([1, 2, 4]), True),
            ([1, 2, 3], [1, 2, 4], True),
        ],
    )
    def test_ne(self, list1, list2, expected):
        cl1 = CustomList(list1)
        if isinstance(list2, CustomList):
            cl2 = list2
        else:
            cl2 = CustomList(list2) if isinstance(list2, list) else list2

        assert (cl1 != cl2) == expected
        if isinstance(cl2, (CustomList, list)):
            assert (cl2 != cl1) == expected

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [1, 2, 4], True),
            ([1, 2, 3], [1, 2, 2], False),
            ([1, 2, 3], [1, 2, 3], False),
            ([1, 2, 3], [6], False),
            ([], [1], True),
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
            ([1, 2, 3], [6], True),
            ([], [1], True),
            ([], [], True),
        ],
    )
    def test_le(self, list1, list2, expected):
        cl1 = CustomList(list1)
        cl2 = CustomList(list2)
        assert (cl1 <= cl2) == expected

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [1, 2, 2], True),
            ([1, 2, 3], [1, 2, 3], False),
            ([1, 2, 3], [1, 2, 4], False),
            ([6], [1, 2, 3], False),
            ([1], [], True),
        ],
    )
    def test_gt(self, list1, list2, expected):
        cl1 = CustomList(list1)
        cl2 = CustomList(list2)
        assert (cl1 > cl2) == expected

    @pytest.mark.parametrize(
        "list1, list2, expected",
        [
            ([1, 2, 3], [1, 2, 2], True),
            ([1, 2, 3], [1, 2, 3], True),
            ([1, 2, 3], [1, 2, 4], False),
            ([6], [1, 2, 3], True),
            ([1], [], True),
            ([], [], True),
        ],
    )
    def test_ge(self, list1, list2, expected):
        cl1 = CustomList(list1)
        cl2 = CustomList(list2)
        assert (cl1 >= cl2) == expected

    def test_str(self):
        cl = CustomList([1, 2, 3])
        assert str(cl) == "1 2 3 Сумма: 6"
        assert str(CustomList([])) == " Сумма: 0"

    def test_comparison_with_regular_list(self):
        cl = CustomList([1, 2, 3])
        regular_list = [1, 2, 3]

        assert (cl == regular_list) is True
        assert (cl != regular_list) is False
        assert (cl < [1, 2, 4]) is True
        assert (cl <= [1, 2, 3]) is True
        assert (cl > [1, 2, 2]) is True
        assert (cl >= [1, 2, 3]) is True
