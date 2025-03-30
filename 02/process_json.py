import json


def check_token_in_values(token, values):
    token_lower = token.lower()
    values_lower = [value.lower() for value in values]
    return token_lower in values_lower


def create_dict_from_str(json_str):
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            raise ValueError("Строка должна представлять JSON-словарь")
        json_dict = {}
        for key, value in data.items():
            if isinstance(value, str):
                json_dict[key] = value.split()
            else:
                raise ValueError("Значения в JSON должны быть строками")

        return json_dict

    except json.JSONDecodeError as e:
        raise ValueError(f"Ошибка декодирования JSON: {e}")
    except ValueError as e:
        raise ValueError(str(e))


def process_json(
    json_str: str,
    required_keys: list[str] | None = None,
    tokens: list[str] | None = None,
    callback=None
) -> None:
    if required_keys is None:
        required_keys = []
    if tokens is None:
        tokens = []

    try:
        json_dict = create_dict_from_str(json_str)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    for key, value in json_dict.items():
        if key in required_keys:
            for token in tokens:
                if check_token_in_values(token, value):
                    if callback:
                        print(callback(key, token))
                    else:  # Удалим f-строку
                        print(f"{key}: {token}")


json_str = '{"key1": "Word1 word2", "key2": "word2 word3"}'
required_keys = ["key1", "KEY2"]
tokens = ["WORD1", "word2"]

process_json(json_str, required_keys, tokens, lambda key, token: f"{key=}, {token=}")
# выведет:
# key="key1", token="WORD1"
# key="key1", token="word2