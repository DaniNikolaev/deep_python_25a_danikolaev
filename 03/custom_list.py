

class CustomList(list):

    def __add__(self, other):
        if isinstance(other, int):
            values = [v + other for v in self]
            return CustomList(values)
        if type(other) in (list, CustomList):
            diff = len(self) - len(other)
            if diff == 0:
                values = [v + o for v, o in zip(self, other)]
                return CustomList(values)
            if diff < 0:
                self.extend([0] * (len(other) - len(self)))
                values = [v + o for v, o in zip(self, other)]
                return CustomList(values)
            if diff > 0:
                other.extend([0] * (len(self) - len(other)))
                values = [v + o for v, o in zip(self, other)]
                return CustomList(values)
        return None

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, int):
            values = [v - other for v in self]
            return CustomList(values)
        if type(other) in (list, CustomList):
            diff = len(self) - len(other)
            if diff == 0:
                values = [v - o for v, o in zip(self, other)]
                return CustomList(values)
            if diff < 0:
                temp_values = self.copy()
                temp_values.extend([0] * (len(other) - len(self)))
                values = [v - o for v, o in zip(temp_values, other)]
                return CustomList(values)
            if diff > 0:
                temp_values = other.copy()
                temp_values.extend([0] * (len(self) - len(other)))
                values = [v - o for v, o in zip(self, temp_values)]
                return CustomList(values)
        return None

    def __rsub__(self, other):
        if isinstance(other, int):
            values = [other - v for v in self]
            return CustomList(values)
        if type(other) in (list, CustomList):
            diff = len(self) - len(other)
            if diff == 0:
                values = [o - v for v, o in zip(self, other)]
                return CustomList(values)
            if diff < 0:
                temp_values = self.copy()
                temp_values.extend([0] * (len(other) - len(self)))
                values = [o - v for v, o in zip(temp_values, other)]
                return CustomList(values)
            if diff > 0:
                temp_values = other.copy()
                temp_values.extend([0] * (len(self) - len(other)))
                values = [o - v for v, o in zip(self, temp_values)]
                return CustomList(values)
        return None

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
