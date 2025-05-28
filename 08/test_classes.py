import pytest
from classes import (IntWrapper, NormalClass, SlotsClass, WeakrefClass,
                     access_attributes, create_instances)


class TestClasses:
    def test_normal_class_creation(self):
        obj = NormalClass(1, 2, 3)
        assert obj.a == 1
        assert obj.b == 2
        assert obj.c == 3

    def test_slots_class_creation(self):
        obj = SlotsClass(1, 2, 3)
        assert obj.a == 1
        assert obj.b == 2
        assert obj.c == 3

    def test_weakref_class_creation(self):
        obj = WeakrefClass(1, 2, 3)
        assert obj.get_a() == 1
        assert obj.get_b() == 2
        assert obj.get_c() == 3

    def test_int_wrapper(self):
        wrapper = IntWrapper(42)
        assert wrapper.value == 42


class TestInstanceCreation:
    def test_create_normal_instances(self):
        instances = create_instances(NormalClass, 10)
        assert len(instances) == 10
        assert all(isinstance(x, NormalClass) for x in instances)

    def test_create_slots_instances(self):
        instances = create_instances(SlotsClass, 10)
        assert len(instances) == 10
        assert all(isinstance(x, SlotsClass) for x in instances)

    def test_create_weakref_instances(self):
        instances = create_instances(WeakrefClass, 10)
        assert len(instances) == 10
        assert all(isinstance(x, WeakrefClass) for x in instances)


class TestAttributeAccess:
    @pytest.fixture
    def sample_instances(self):
        return {
            'normal': NormalClass(1, 2, 3),
            'slots': SlotsClass(1, 2, 3),
            'weakref': WeakrefClass(1, 2, 3)
        }

    def test_normal_attribute_access(self, sample_instances):
        obj = sample_instances['normal']
        assert obj.a == 1
        assert obj.b == 2
        assert obj.c == 3

    def test_slots_attribute_access(self, sample_instances):
        obj = sample_instances['slots']
        assert obj.a == 1
        assert obj.b == 2
        assert obj.c == 3

    def test_weakref_attribute_access(self, sample_instances):
        obj = sample_instances['weakref']
        assert obj.get_a() == 1
        assert obj.get_b() == 2
        assert obj.get_c() == 3


class TestPerformance:
    def test_create_performance(self):
        create_instances(NormalClass, 10)
        create_instances(SlotsClass, 10)
        create_instances(WeakrefClass, 10)

    def test_access_performance(self):
        normal = create_instances(NormalClass, 10)
        slots = create_instances(SlotsClass, 10)
        weakref = create_instances(WeakrefClass, 10)

        access_attributes(normal)
        access_attributes(slots)
        access_attributes(weakref)


class TestMemoryUsage:
    def test_memory_measurement(self):
        create_instances(NormalClass, 10)
        create_instances(SlotsClass, 10)
        create_instances(WeakrefClass, 10)


def test_access_attributes_function():
    normal = [NormalClass(1, 2, 3) for _ in range(3)]
    slots = [SlotsClass(1, 2, 3) for _ in range(3)]
    weakref = [WeakrefClass(1, 2, 3) for _ in range(3)]

    access_attributes(normal)
    access_attributes(slots)
    access_attributes(weakref)

    for obj in normal:
        assert obj.a == 2
        assert obj.b == 3
        assert obj.c == 4

    for obj in weakref:
        assert obj.get_a() == 2
        assert obj.get_b() == 3
        assert obj.get_c() == 4
