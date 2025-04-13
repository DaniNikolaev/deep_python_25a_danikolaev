from itertools import zip_longest


class CustomList(list):

    @staticmethod
    def __calculate_values(val1, val2, op, r_op):
        if op == '+':
            return val1 + val2
        return val2 - val1 if r_op else val1 - val2

    def __process_operation(self, other, op='+', r_op=False):
        if isinstance(other, int):
            return CustomList([self.__calculate_values(v, other, op, r_op) for v in self])

        if isinstance(other, (list, CustomList)):
            return CustomList([
                self.__calculate_values(v1, v2, op, r_op)
                for v1, v2 in zip_longest(self, other, fillvalue=0)
            ])

        return None

    def __add__(self, other):
        return self.__process_operation(other)

    def __radd__(self, other):
        return self.__process_operation(other, r_op=True)

    def __sub__(self, other):
        return self.__process_operation(other, op='-')

    def __rsub__(self, other):
        return self.__process_operation(other, op='-', r_op=True)

    def __eq__(self, other):
        return sum(self) == sum(other)

    def __ne__(self, other):
        return sum(self) != sum(other)

    def __lt__(self, other):
        return sum(self) < sum(other)

    def __le__(self, other):
        return sum(self) <= sum(other)

    def __gt__(self, other):
        return sum(self) > sum(other)

    def __ge__(self, other):
        return sum(self) >= sum(other)

    def __str__(self):
        return f"{' '.join(map(str, self))} Сумма: {sum(self)}"
