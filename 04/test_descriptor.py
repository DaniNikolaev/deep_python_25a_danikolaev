from unittest.mock import patch
import pytest
from descriptor import Age, Height, Name, Position, FootballPlayer


class TestAge:
    def test_check_value_valid(self):
        age = Age(min_age=16, max_age=40)
        assert age.check_value(20) is True

    def test_check_value_min_boundary(self):
        age = Age(min_age=16, max_age=40)
        assert age.check_value(16) is True

    def test_check_value_max_boundary(self):
        age = Age(min_age=16, max_age=40)
        assert age.check_value(40) is True

    def test_check_value_too_low(self):
        age = Age(min_age=16, max_age=40)
        with pytest.raises(ValueError, match="Возраст должен быть в интервале: 16 - 40"):
            age.check_value(15)

    def test_check_value_too_high(self):
        age = Age(min_age=16, max_age=40)
        with pytest.raises(ValueError, match="Возраст должен быть в интервале: 16 - 40"):
            age.check_value(41)

    def test_check_value_not_int(self):
        age = Age(min_age=16, max_age=40)
        with pytest.raises(ValueError, match="Возраст должен быть целым числом!"):
            age.check_value("20")

    def test_descriptor_behavior(self):
        class TestClass:
            age = Age()

        obj = TestClass()
        obj.age = 25
        assert obj.age == 25

        with pytest.raises(ValueError):
            obj.age = "invalid"

    def test_instance_independence(self):
        class TestClass:
            age = Age(min_age=16, max_age=40)

        obj1 = TestClass()
        obj2 = TestClass()

        obj1.age = 20
        obj2.age = 25

        assert obj1.age == 20
        assert obj2.age == 25

        obj1.age = 30
        assert obj1.age == 30
        assert obj2.age == 25

    def test_invalid_value_not_set(self):
        class TestClass:
            age = Age(min_age=16, max_age=40)

        obj = TestClass()
        obj.age = 25
        assert obj.age == 25

        with pytest.raises(ValueError):
            obj.age = "invalid"

        assert obj.age == 25

    def test_valid_value_change(self):
        class TestClass:
            age = Age(min_age=16, max_age=40)

        obj = TestClass()
        obj.age = 20
        assert obj.age == 20

        obj.age = 25
        assert obj.age == 25


class TestHeight:
    def test_check_value_valid_int(self):
        height = Height(min_height=165.0)
        assert height.check_value(170) is True

    def test_check_value_valid_float(self):
        height = Height(min_height=165.0)
        assert height.check_value(170.5) is True

    def test_check_value_min_boundary(self):
        height = Height(min_height=165.0)
        assert height.check_value(165.0) is True

    def test_check_value_too_low(self):
        height = Height(min_height=165.0)
        with pytest.raises(ValueError, match="Рост должен быть больше или равен 165.0!"):
            height.check_value(160.0)

    def test_check_value_not_number(self):
        height = Height(min_height=165.0)
        with pytest.raises(ValueError, match="Рост должен быть числом!"):
            height.check_value("170")

    def test_descriptor_behavior(self):
        class TestClass:
            height = Height()

        obj = TestClass()
        obj.height = 175.5
        assert obj.height == 175.5

        with pytest.raises(ValueError):
            obj.height = "invalid"

    def test_instance_independence(self):
        class TestClass:
            height = Height(min_height=165.0)

        obj1 = TestClass()
        obj2 = TestClass()

        obj1.height = 170.0
        obj2.height = 180.0

        assert obj1.height == 170.0
        assert obj2.height == 180.0

        obj1.height = 175.0
        assert obj1.height == 175.0
        assert obj2.height == 180.0

    def test_invalid_value_not_set(self):
        class TestClass:
            height = Height(min_height=165.0)

        obj = TestClass()
        obj.height = 170.0
        assert obj.height == 170.0

        with pytest.raises(ValueError):
            obj.height = "invalid"

        assert obj.height == 170.0

    def test_valid_value_change(self):
        class TestClass:
            height = Height(min_height=165.0)

        obj = TestClass()
        obj.height = 170.0
        assert obj.height == 170.0

        obj.height = 175.0
        assert obj.height == 175.0


class TestName:
    def test_check_value_valid(self):
        name = Name(min_length=3, max_length=50)
        assert name.check_value("Cri") is True

    def test_check_value_min_boundary(self):
        name = Name(min_length=3, max_length=50)
        assert name.check_value("ABC") is True

    def test_check_value_max_boundary(self):
        name = Name(min_length=3, max_length=50)
        long_name = "A" * 50
        assert name.check_value(long_name) is True

    def test_check_value_too_short(self):
        name = Name(min_length=3, max_length=50)
        with pytest.raises(ValueError, match="Длина имения должна быть в диапазоне от 3 до 50"):
            name.check_value("Ro")

    def test_check_value_too_long(self):
        name = Name(min_length=3, max_length=50)
        long_name = "A" * 51
        with pytest.raises(ValueError, match="Длина имения должна быть в диапазоне от 3 до 50"):
            name.check_value(long_name)

    def test_check_value_not_str(self):
        name = Name(min_length=3, max_length=50)
        with pytest.raises(ValueError, match="Имя должно быть строкой!"):
            name.check_value(123)

    def test_descriptor_behavior(self):
        class TestClass:
            name = Name()

        obj = TestClass()
        obj.name = "Cri Ronaldo"
        assert obj.name == "Cri Ronaldo"

        with pytest.raises(ValueError):
            obj.name = 123

    def test_instance_independence(self):
        class TestClass:
            name = Name(min_length=3, max_length=50)

        obj1 = TestClass()
        obj2 = TestClass()

        obj1.name = "Player One"
        obj2.name = "Player Two"

        assert obj1.name == "Player One"
        assert obj2.name == "Player Two"

        obj1.name = "Updated One"
        assert obj1.name == "Updated One"
        assert obj2.name == "Player Two"

    def test_invalid_value_not_set(self):
        class TestClass:
            name = Name(min_length=3, max_length=50)

        obj = TestClass()
        obj.name = "Valid Name"
        assert obj.name == "Valid Name"

        with pytest.raises(ValueError):
            obj.name = 123

        assert obj.name == "Valid Name"

    def test_valid_value_change(self):
        class TestClass:
            name = Name(min_length=3, max_length=50)

        obj = TestClass()
        obj.name = "First Name"
        assert obj.name == "First Name"

        obj.name = "Second Name"
        assert obj.name == "Second Name"


class TestPosition:
    def test_check_value_valid(self):
        position = Position()
        for pos in position.POSITIONS:
            assert position.check_value(pos) is True

    def test_check_value_invalid(self):
        position = Position()
        with pytest.raises(ValueError, match="Такой позиции не существует!"):
            position.check_value("INVALID")

    def test_check_value_not_str(self):
        position = Position()
        with pytest.raises(ValueError, match="Позиция должна быть строкой!"):
            position.check_value(123)

    def test_descriptor_behavior(self):
        class TestClass:
            position = Position()

        obj = TestClass()
        obj.position = "CM"
        assert obj.position == "CM"

        with pytest.raises(ValueError):
            obj.position = "INVALID"

    def test_instance_independence(self):
        class TestClass:
            position = Position()

        obj1 = TestClass()
        obj2 = TestClass()

        obj1.position = "CM"
        obj2.position = "GK"

        assert obj1.position == "CM"
        assert obj2.position == "GK"

        obj1.position = "CB"
        assert obj1.position == "CB"
        assert obj2.position == "GK"

    def test_invalid_value_not_set(self):
        class TestClass:
            position = Position()

        obj = TestClass()
        obj.position = "CM"
        assert obj.position == "CM"

        with pytest.raises(ValueError):
            obj.position = "INVALID"

        assert obj.position == "CM"

    def test_valid_value_change(self):
        class TestClass:
            position = Position()

        obj = TestClass()
        obj.position = "CM"
        assert obj.position == "CM"

        obj.position = "GK"
        assert obj.position == "GK"


class TestFootballPlayer:
    def test_valid_player_creation(self):
        player = FootballPlayer(name="Lionel Messi", age=35, height=170.0, position="RW")
        assert player.name == "Lionel Messi"
        assert player.age == 35
        assert player.height == 170.0
        assert player.position == "RW"
        assert player.name == "Lionel Messi"
        assert player.age == 35
        assert player.height == 170.0
        assert player.position == "RW"

    def test_invalid_name(self):
        with pytest.raises(ValueError):
            FootballPlayer(name=123, age=35, height=170.0, position="RW")

    def test_invalid_age(self):
        with pytest.raises(ValueError):
            FootballPlayer(name="Lionel Messi", age="35", height=170.0, position="RW")

    def test_invalid_height(self):
        with pytest.raises(ValueError):
            FootballPlayer(name="Lionel Messi", age=35, height="170.0", position="RW")

    def test_invalid_position(self):
        with pytest.raises(ValueError):
            FootballPlayer(name="Lionel Messi", age=35, height=170.0, position="INVALID")

    @patch('descriptor.Name.check_value')
    @patch('descriptor.Age.check_value')
    @patch('descriptor.Height.check_value')
    @patch('descriptor.Position.check_value')
    def test_check_value_calls(self, mock_pos, mock_height, mock_age, mock_name):
        mock_name.return_value = True
        mock_age.return_value = True
        mock_height.return_value = True
        mock_pos.return_value = True

        FootballPlayer(name="Test", age=25, height=180.0, position="CM")

        mock_name.assert_called_once_with("Test")
        mock_age.assert_called_once_with(25)
        mock_height.assert_called_once_with(180.0)
        mock_pos.assert_called_once_with("CM")

    def test_custom_age_range(self):
        class CustomPlayer:
            age = Age(min_age=18, max_age=45)

        player = CustomPlayer()
        player.age = 20
        assert player.age == 20

        with pytest.raises(ValueError):
            player.age = 16

    def test_custom_height(self):
        class CustomPlayer:
            height = Height(min_height=170.0)

        player = CustomPlayer()
        player.height = 175.0
        assert player.height == 175.0

        with pytest.raises(ValueError):
            player.height = 160.0

    def test_custom_name_length(self):
        class CustomPlayer:
            name = Name(min_length=5, max_length=30)

        player = CustomPlayer()
        player.name = "Valid Name"
        assert player.name == "Valid Name"

        with pytest.raises(ValueError):
            player.name = "Tiny"

    def test_instance_independence(self):
        player1 = FootballPlayer(name="Player One", age=20, height=170.0, position="CM")
        player2 = FootballPlayer(name="Player Two", age=25, height=180.0, position="GK")

        assert player1.name == "Player One"
        assert player2.name == "Player Two"

        player1.name = "Updated One"
        assert player1.name == "Updated One"
        assert player2.name == "Player Two"

    def test_invalid_value_not_set(self):
        player = FootballPlayer(name="Valid Name", age=25, height=175.0, position="CM")

        original_name = player.name
        with pytest.raises(ValueError):
            player.name = 123

        assert player.name == original_name

    def test_valid_value_change(self):
        player = FootballPlayer(name="Original Name", age=25, height=175.0, position="CM")

        player.name = "New Name"
        assert player.name == "New Name"

        player.age = 26
        assert player.age == 26

        player.height = 176.0
        assert player.height == 176.0

        player.position = "GK"
        assert player.position == "GK"

    def test_field_specific_error_messages(self):
        with pytest.raises(ValueError) as exc_info:
            FootballPlayer(name=123, age=25, height=175.0, position="CM")
        assert "Имя должно быть строкой!" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            FootballPlayer(name="Valid", age="25", height=175.0, position="CM")
        assert "Возраст должен быть целым числом!" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            FootballPlayer(name="Valid", age=25, height="175.0", position="CM")
        assert "Рост должен быть числом!" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            FootballPlayer(name="Valid", age=25, height=175.0, position=123)
        assert "Позиция должна быть строкой!" in str(exc_info.value)
