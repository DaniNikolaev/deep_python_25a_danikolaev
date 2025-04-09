class CustomMeta(type):
    def __new__(mcs, name, bases, namespace):
        new_namespace = {}
        for attr_name, attr_value in namespace.items():
            if not (attr_name.startswith('__') and attr_name.endswith('__')):
                new_namespace[f'custom_{attr_name}'] = attr_value
            else:
                new_namespace[attr_name] = attr_value

        cls = super().__new__(mcs, name, bases, new_namespace)

        def __setattr__(self, __name, value):
            if not (__name.startswith('__') and __name.endswith('__')):
                if __name.startswith('custom_'):
                    object.__setattr__(self, __name, value)
                else:
                    object.__setattr__(self, f'custom_{__name}', value)
            else:
                object.__setattr__(self, __name, value)

        cls.__setattr__ = __setattr__
        return cls

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        def __getattribute__(self, __name):
            if not (__name.startswith('__') and __name.endswith('__')):
                if not __name.startswith('custom_'):
                    raise AttributeError(
                        f"'{self.__class__.__name__}' object has no attribute '{__name}'"
                    )
            return object.__getattribute__(self, __name)

        cls.__getattribute__ = __getattribute__


class CustomClass(metaclass=CustomMeta):
    x = 50

    def __init__(self, val=99):
        self.val = val

    def line(self):
        return 100

    def __str__(self):
        return "Custom_by_metaclass"
