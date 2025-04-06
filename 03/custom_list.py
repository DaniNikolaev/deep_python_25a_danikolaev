

class CustomList(list):

    def __calculate(self, other, op='+', r_op=False):
        if isinstance(other, int):
            if op == '+':
                values = [v + other for v in self]
            else:
                if r_op:
                    values = [other - v for v in self]
                else:
                    values = [v - other for v in self]
            return CustomList(values)
        if type(other) in (list, CustomList):
            diff = len(self) - len(other)
            if diff == 0:
                if op == '+':
                    values = [v + o for v, o in zip(self, other)]
                else:
                    if r_op:
                        values = [o - v for v, o in zip(self, other)]
                    else:
                        values = [v - o for v, o in zip(self, other)]
                return CustomList(values)
            if diff < 0:
                self_copy = self.copy()
                self_copy.extend([0] * (-diff))
                if op == '+':
                    values = [v + o for v, o in zip(self_copy, other)]
                else:
                    if r_op:
                        values = [o - v for v, o in zip(self_copy, other)]
                    else:
                        values = [v - o for v, o in zip(self_copy, other)]
                return CustomList(values)
            if diff > 0:
                other_copy = other.copy()
                other_copy.extend([0] * diff)
                if op == '+':
                    values = [v + o for v, o in zip(self, other_copy)]
                else:
                    if r_op:
                        values = [o - v for v, o in zip(self, other_copy)]
                    else:
                        values = [v - o for v, o in zip(self, other_copy)]
                return CustomList(values)
        return None

    def __add__(self, other):
        return self.__calculate(other)

    def __radd__(self, other):
        return self.__calculate(other, r_op=True)

    def __sub__(self, other):
        return self.__calculate(other, op='-')

    def __rsub__(self, other):
        return self.__calculate(other, op='-', r_op=True)

    def __eq__(self, other):
        return sum(self) == sum(other)

    def __lt__(self, other):
        return sum(self) < sum(other)

    def __le__(self, other):
        return sum(self) <= sum(other)

    def __str__(self):
        s = ''
        for v in self:
            s += str(v) + ' '
        return s + 'Сумма: ' + str(sum(self))
