# pylint: disable=no-member,attribute-defined-outside-init
import pytest
from metaclass import CustomClass, CustomMeta


class TestCustomMetaGeneral:

    def test_empty_class(self):

        class Empty(metaclass=CustomMeta):
            pass

        assert not hasattr(Empty, '__dict__') or not Empty.__dict__.get('custom__dict__')

    def test_class_with_attributes(self):

        class TestClass(metaclass=CustomMeta):
            val = 50

            def method(self):
                return "test"

        assert TestClass.custom_val == 50
        assert TestClass.custom_method(None) == "test"
        with pytest.raises(AttributeError):
            _ = TestClass.val
        with pytest.raises(AttributeError):
            TestClass.method(self)

    def test_dynamic_attributes(self):

        class TestClass(metaclass=CustomMeta):
            pass

        inst = TestClass()
        inst.dynamic = "value"
        assert inst.custom_dynamic == "value"
        with pytest.raises(AttributeError):
            _ = inst.dynamic

    def test_inheritance(self):

        class Parent(metaclass=CustomMeta):
            parent_attr = 1

        class Child(Parent):
            child_attr = 2

        assert Child.custom_parent_attr == 1
        assert Child.custom_child_attr == 2
        with pytest.raises(AttributeError):
            _ = Child.parent_attr

    def test_setattr_behavior(self):

        class TestClass(metaclass=CustomMeta):
            pass

        obj = TestClass()

        obj.test_attr = 100
        assert not hasattr(obj, 'test_attr')
        assert obj.custom_test_attr == 100

        obj.custom_test_attr = 200
        assert obj.custom_test_attr == 200

        obj.__dict__['magic'] = 300
        assert obj.__dict__['magic'] == 300

    def test_getattribute_behavior(self):

        class TestClass(metaclass=CustomMeta):
            cls_attr = 10

            def __init__(self):
                self.inst_attr = 20

        obj = TestClass()

        assert obj.custom_cls_attr == 10
        assert obj.custom_inst_attr == 20

        with pytest.raises(AttributeError):
            _ = obj.cls_attr
        with pytest.raises(AttributeError):
            _ = obj.inst_attr

        assert isinstance(obj, TestClass)
        assert str(obj).startswith('<')

        with pytest.raises(AttributeError):
            _ = obj.non_existent


class TestCustomClass:

    def test_standard_attributes(self):
        assert CustomClass.custom_x == 50
        with pytest.raises(AttributeError):
            _ = CustomClass.x

    def test_instance_behavior(self):
        inst = CustomClass(val=200)
        assert inst.custom_val == 200
        assert inst.custom_line() == 100
        with pytest.raises(AttributeError):
            _ = inst.val

    def test_magic_methods(self):
        inst = CustomClass()
        assert str(inst) == "Custom_by_metaclass"
        assert isinstance(inst, CustomClass)

    def test_dynamic_attributes(self):
        inst = CustomClass()
        inst.new_attr = 500
        assert inst.custom_new_attr == 500
        with pytest.raises(AttributeError):
            _ = inst.new_attr

    def test_setattr_on_custom_class(self):
        inst = CustomClass()

        inst.dynamic_attr = 500
        assert inst.custom_dynamic_attr == 500
        with pytest.raises(AttributeError):
            _ = inst.dynamic_attr

        inst.custom_val = 300
        assert inst.custom_val == 300

    def test_getattribute_on_custom_class(self):
        inst = CustomClass(val=150)

        assert inst.custom_val == 150
        assert inst.custom_line() == 100

        with pytest.raises(AttributeError):
            _ = inst.val
        with pytest.raises(AttributeError):
            inst.line()

        assert str(inst) == "Custom_by_metaclass"
