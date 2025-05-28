import timeit
import tracemalloc
import weakref

NUM_INSTANCES = 100_000


class NormalClass:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


class SlotsClass:
    __slots__ = ('a', 'b', 'c')

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


class IntWrapper:
    def __init__(self, value):
        self.value = value


class WeakrefClass:
    def __init__(self, a, b, c):
        self._int_wrappers = [
            IntWrapper(a),
            IntWrapper(b),
            IntWrapper(c)
        ]

        self.a = weakref.ref(self._int_wrappers[0])
        self.b = weakref.ref(self._int_wrappers[1])
        self.c = weakref.ref(self._int_wrappers[2])

    def get_a(self):
        ref = self.a()
        return ref.value if ref else None

    def get_b(self):
        ref = self.b()
        return ref.value if ref else None

    def get_c(self):
        ref = self.c()
        return ref.value if ref else None


def create_instances(cls, num_instances):
    return [cls(i, i * 2, i * 3) for i in range(num_instances)]


def access_attributes(instances):
    for instance in instances:
        if isinstance(instance, WeakrefClass):
            x = instance.get_a()
            y = instance.get_b()
            z = instance.get_c()

            if x is not None:
                instance.a().value = x + 1
            if y is not None:
                instance.b().value = y + 1
            if z is not None:
                instance.c().value = z + 1
        else:
            x = instance.a
            y = instance.b
            z = instance.c
            instance.a = x + 1
            instance.b = y + 1
            instance.c = z + 1


def main():
    time_normal_create = timeit.timeit(lambda: create_instances(NormalClass, NUM_INSTANCES), number=1)
    time_slots_create = timeit.timeit(lambda: create_instances(SlotsClass, NUM_INSTANCES), number=1)
    time_weakref_create = timeit.timeit(lambda: create_instances(WeakrefClass, NUM_INSTANCES), number=1)

    normal_instances = create_instances(NormalClass, NUM_INSTANCES)
    slots_instances = create_instances(SlotsClass, NUM_INSTANCES)
    weakref_instances = create_instances(WeakrefClass, NUM_INSTANCES)

    time_normal_access = timeit.timeit(lambda: access_attributes(normal_instances), number=1)
    time_slots_access = timeit.timeit(lambda: access_attributes(slots_instances), number=1)
    time_weakref_access = timeit.timeit(lambda: access_attributes(weakref_instances), number=1)

    tracemalloc.start()
    normal_instances = create_instances(NormalClass, NUM_INSTANCES)
    normal_size = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    tracemalloc.start()
    slots_instances = create_instances(SlotsClass, NUM_INSTANCES)
    slots_size = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    tracemalloc.start()
    weakref_instances = create_instances(WeakrefClass, NUM_INSTANCES)
    weakref_size = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()

    print(f"Время создания NormalClass: {time_normal_create:.4f} сек")
    print(f"Время создания SlotsClass: {time_slots_create:.4f} сек")
    print(f"Время создания WeakrefClass: {time_weakref_create:.4f} сек")

    print(f"Время доступа к атрибутам NormalClass: {time_normal_access:.4f} сек")
    print(f"Время доступа к атрибутам SlotsClass: {time_slots_access:.4f} сек")
    print(f"Время доступа к атрибутам WeakrefClass: {time_weakref_access:.4f} сек")

    print(f"Размер NormalClass: {normal_size} байт")
    print(f"Размер SlotsClass: {slots_size} байт")
    print(f"Размер WeakrefClass: {weakref_size} байт")


if __name__ == '__main__':
    main()
