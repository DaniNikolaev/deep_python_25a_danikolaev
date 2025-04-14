from abc import ABC, abstractmethod


class Base(ABC):
    def __init__(self):
        self.name = '_'

    @abstractmethod
    def check_value(self, value):
        pass

    def __set_name__(self, instance, name):
        self.name += name

    def __get__(self, instance, owner):
        if instance is None:
            return None
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        if self.check_value(value):
            setattr(instance, self.name, value)


class Age(Base):
    def __init__(self, min_age=16, max_age=40):
        super().__init__()
        self.min_age = min_age
        self.max_age = max_age

    def check_value(self, value):
        if isinstance(value, int):
            if self.min_age <= value <= self.max_age:
                return True
            raise ValueError(f'Возраст должен быть в интервале: {self.min_age} - {self.max_age}')
        raise ValueError('Возраст должен быть целым числом!')


class Height(Base):
    def __init__(self, min_height=165.0):
        super().__init__()
        self.min_height = min_height

    def check_value(self, value):
        if isinstance(value, (int, float)):
            if value >= self.min_height:
                return True
            raise ValueError(f'Рост должен быть больше или равен {self.min_height}!')
        raise ValueError('Рост должен быть числом!')


class Name(Base):
    def __init__(self, min_length=3, max_length=50):
        super().__init__()
        self.min_length = min_length
        self.max_length = max_length

    def check_value(self, value):
        if isinstance(value, str):
            if self.min_length <= len(value) <= self.max_length:
                return True
            raise ValueError(f'Длина имения должна быть в диапазоне от {self.min_length} до {self.max_length}')
        raise ValueError('Имя должно быть строкой!')


class Position(Base):
    POSITIONS = ('GK', 'LB', 'CB', 'RB', 'LM', 'CM', 'CDM', 'CAM', 'RM', 'LW', 'CF', 'RW', 'ST')

    def check_value(self, value):
        if isinstance(value, str):
            if value in self.POSITIONS:
                return True
            raise ValueError('Такой позиции не существует!')
        raise ValueError('Позиция должна быть строкой!')


class FootballPlayer:
    name = Name()
    age = Age()
    height = Height()
    position = Position()

    def __init__(self, name, age, height, position):
        self.name = name
        self.age = age
        self.height = height
        self.position = position
