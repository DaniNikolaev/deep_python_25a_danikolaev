def check_line(line, search_words, stop_words):
    if not line:
        return
    line = line.strip()
    if any(map(lambda x: x in stop_words, [v.lower() for v in line.split()])):
        return
    if any(map(lambda x: x in search_words, [v.lower() for v in line.split()])):
        yield line


def search_in_file(filename, search_words, stop_words):
    stop_words = [word.lower() for word in stop_words]
    search_words = [word.lower() for word in search_words]
    try:
        if isinstance(filename, str):
            with open(filename, mode='r', encoding='utf-8') as file:
                for line in file:
                    yield from check_line(line, search_words, stop_words)
        else:
            for line in filename:
                yield from check_line(line, search_words, stop_words)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f'Файл не найден: {filename}') from exc
