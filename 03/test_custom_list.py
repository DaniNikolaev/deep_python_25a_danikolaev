from unittest.mock import patch
from custom_list import CustomList


class TestCustomList:

    def test_add_int(self):
        cl = CustomList([1, 2, 3])
        result = cl + 2
        assert result == CustomList([3, 4, 5])

    def test_add_list_equal_length(self):
        cl = CustomList([1, 2, 3])
        other = [4, 5, 6]
        result = cl + other
        assert result == CustomList([5, 7, 9])

    def test_add_customlist_equal_length(self):
        cl = CustomList([1, 2, 3])
        other = CustomList([4, 5, 6])
        result = cl + other
        assert result == CustomList([5, 7, 9])

    def test_add_list_shorter(self):
        cl = CustomList([1, 2, 3])
        other = [4, 5]
        result = cl + other
        assert result == CustomList([5, 7, 3])

    def test_add_list_longer(self):
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        result = cl + other
        assert result == CustomList([5, 7, 6])

    def test_add_invalid_type(self):
        cl = CustomList([1, 2, 3])
        result = cl + "string"
        assert result is None

    def test_radd_int(self):
        cl = CustomList([1, 2, 3])
        result = 2 + cl
        assert result == CustomList([3, 4, 5])

    def test_radd_list(self):
        cl = CustomList([1, 2, 3])
        other = [4, 5, 6]
        result = other + cl
        assert result == CustomList([5, 7, 9])

    def test_sub_int(self):
        cl = CustomList([1, 2, 3])
        result = cl - 2
        assert result == CustomList([-1, 0, 1])

    def test_sub_list_equal_length(self):
        cl = CustomList([1, 2, 3])
        other = [4, 5, 6]
        result = cl - other
        assert result == CustomList([-3, -3, -3])

    def test_sub_customlist_equal_length(self):
        cl = CustomList([1, 2, 3])
        other = CustomList([4, 5, 6])
        result = cl - other
        assert result == CustomList([-3, -3, -3])

    def test_sub_list_shorter(self):
        cl = CustomList([1, 2, 3])
        other = [4, 5]
        result = cl - other
        assert result == CustomList([-3, -3, 3])

    def test_sub_list_longer(self):
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        result = cl - other
        assert result == CustomList([-3, -3, -6])

    def test_rsub_list_equal_length(self):
        cl = CustomList([1, 2, 3])
        other = [4, 5, 6]
        result = other - cl
        assert result == CustomList([3, 3, 3])

    def test_rsub_list_shorter(self):
        cl = CustomList([1, 2, 3])
        other = [4, 5]
        result = other - cl
        assert result == CustomList([3, 3, -3])

    def test_rsub_list_longer(self):
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        result = other - cl
        assert result == CustomList([3, 3, 6])

    def test_sub_invalid_type(self):
        cl = CustomList([1, 2, 3])
        result = cl - "string"
        assert result is None

    def test_rsub_int(self):
        cl = CustomList([1, 2, 3])
        result = 5 - cl
        assert result == CustomList([4, 3, 2])

    def test_eq_true(self):
        cl1 = CustomList([1, 2, 3])
        cl2 = CustomList([3, 2, 1])
        assert cl1 == cl2

    def test_eq_false(self):
        cl1 = CustomList([1, 2, 3])
        cl2 = CustomList([1, 2, 4])
        assert cl1 != cl2

    def test_lt_true(self):
        cl1 = CustomList([1, 2, 3])
        cl2 = CustomList([1, 2, 4])
        assert cl1 < cl2

    def test_lt_false(self):
        cl1 = CustomList([1, 2, 3])
        cl2 = CustomList([1, 2, 2])
        assert cl1 >= cl2
        cl2 = CustomList([1, 2, 3])
        assert cl1 >= cl2

    def test_le_true(self):
        cl1 = CustomList([1, 2, 3])
        cl2 = CustomList([1, 2, 4])
        assert cl1 <= cl2
        cl2 = CustomList([1, 2, 3])
        assert cl1 <= cl2

    def test_le_false(self):
        cl1 = CustomList([1, 2, 3])
        cl2 = CustomList([1, 2, 2])
        assert cl1 > cl2

    def test_str(self):
        cl = CustomList([1, 2, 3])
        assert str(cl) == "1 2 3 Сумма: 6"

    def test_add_extend_side_effect(self):
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        with patch("custom_list.CustomList.extend") as mock_extend:
            cl + other
            mock_extend.assert_called_once_with([0])

    def test_sub_extend_side_effect(self):
        """Тест, проверяющий, что extend вызывается с правильным аргументом"""
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        with patch("custom_list.CustomList.extend") as mock_extend:
            cl - other
            mock_extend.assert_not_called()

    def test_rsub_extend_side_effect(self):
        """Тест, проверяющий, что extend вызывается с правильным аргументом"""
        cl = CustomList([1, 2])
        other = [4, 5, 6]
        with patch("custom_list.CustomList.extend") as mock_extend:
            other - cl
            mock_extend.assert_not_called()
