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

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def get(self, key):
        if key not in self.cache:
            return None

        node = self.cache[key]
        self.move_to_head(node)
        return node.value

    def set(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self.move_to_head(node)
        else:
            if len(self.cache) >= self.limit:
                tail = self.pop_tail()
                del self.cache[tail.key]

            new_node = Node(key, value)
            self.cache[key] = new_node
            self.add_node(new_node)

    def add_node(self, new_node):
        if self.head is None:
            self.head = self.tail = new_node
        else:
            new_node.next_node = self.head
            self.head.prev_node = new_node
            self.head = new_node

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

    def move_to_head(self, node):
        if node is self.head:
            return
        self.remove_node(node)
        self.add_node(node)

    def pop_tail(self):
        if not self.tail:
            return None
        node = self.tail
        self.remove_node(node)
        return node

    def __str__(self):
        s = ''
        node = self.head
        while node is not None:
            s += str(node) + '\n'
            node = node.next_node
        return s

cache = LRUCache(2)

cache.set("k1", "val1")
cache.set("k2", "val2")

assert cache.get("k3") is None
assert cache.get("k2") == "val2"
assert cache.get("k1") == "val1"

cache.set("k3", "val3")

assert cache.get("k3") == "val3"
assert cache.get("k2") is None
assert cache.get("k1") == "val1"