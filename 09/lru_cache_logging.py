import argparse
import logging
import sys


class EvenWordsFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        word_count = len(message.split())
        return word_count % 2 != 0


class Node:
    __slots__ = ('key', 'value', 'prev_node', 'next_node')

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev_node = self.next_node = None

    def __str__(self):
        return str(f'Node: {self.key}: {self.value}')


class LRUCache:
    def __init__(self, limit=10):
        if limit <= 0:
            raise ValueError("Limit должен быть больше 0")
        self.limit = limit
        self.cache = {}
        self.head = self.tail = None
        self.logger = logging.getLogger('LRUCache')
        self.logger.setLevel(logging.DEBUG)

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, key):
        if key not in self.cache:
            self.logger.warning("Ключ '%s' не найден в кэше", key)
            return None

        node = self.cache[key]
        self.move_to_head(node)
        self.logger.info("Полученный ключ '%s' со значением '%s'", key, node.value)
        self.logger.debug("Состояние кэша после get '%s': %s", key, self._cache_state())
        return node.value

    def set(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self.move_to_head(node)
            self.logger.info("Обновленный ключ '%s' со значением '%s'", key, value)
            self.logger.debug("Состояние кэша после update '%s': %s", key, self._cache_state())
        else:
            if len(self.cache) >= self.limit:
                tail = self.pop_tail()
                del self.cache[tail.key]
                self.logger.warning(
                    "Достигнут limit кэша. Удален node с ключом '%s'", tail.key
                )

            new_node = Node(key, value)
            self.cache[key] = new_node
            self.add_node(new_node)
            self.logger.info("Добавлен новый ключ '%s' со значением '%s'", key, value)
            self.logger.debug("Состояние кэша после add '%s': %s", key, self._cache_state())

    def add_node(self, new_node):
        if self.head is None:
            self.head = self.tail = new_node
            self.logger.debug("Добавлен первый node в кэш")
        else:
            new_node.next_node = self.head
            self.head.prev_node = new_node
            self.head = new_node
            self.logger.debug("Добавлен новый node в голову кэша")

    def remove_node(self, node):
        if node.prev_node:
            node.prev_node.next_node = node.next_node
        else:
            self.head = node.next_node

        if node.next_node:
            node.next_node.prev_node = node.prev_node
        else:
            self.tail = node.prev_node

        node.prev_node = node.next_node = None
        self.logger.debug("Удален node с ключом '%s' из кэша", node.key)

    def move_to_head(self, node):
        if node is self.head:
            return
        self.remove_node(node)
        self.add_node(node)
        self.logger.debug("Сдвинут node с ключом '%s' в голову кэша", node.key)

    def pop_tail(self):
        if not self.tail:
            return None
        node = self.tail
        self.remove_node(node)
        self.logger.debug("Выскочил хвостовый node с ключом '%s'", node.key)
        return node

    def _cache_state(self):
        state = []
        node = self.head
        while node is not None:
            state.append(f"{node.key}:{node.value}")
            node = node.next_node
        return " -> ".join(state)

    def __str__(self):
        s = ''
        node = self.head
        while node is not None:
            s += str(node) + '\n'
            node = node.next_node
        return s


def setup_logging(use_stdout=False, use_filter=False):
    logger = logging.getLogger('LRUCache')
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler('cache.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    if use_filter:
        file_handler.addFilter(EvenWordsFilter())
    logger.addHandler(file_handler)

    if use_stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(
            '[%(levelname)s] %(message)s'
        ))

        if use_filter:
            stdout_handler.addFilter(EvenWordsFilter())

        logger.addHandler(stdout_handler)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store_true', help='Log to stdout')
    parser.add_argument('-f', action='store_true', help='Apply custom filter')
    args = parser.parse_args()

    setup_logging(use_stdout=args.s, use_filter=args.f)

    cache = LRUCache(limit=2)

    cache.set('a', 1)
    cache.set('b', 2)
    cache.set('c', 3)
    cache.get('b')
    cache.get('x')
    cache.set('b', 22)


if __name__ == "__main__":
    main()
