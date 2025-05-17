import time
from unittest.mock import patch

import pytest
from lru_cache import LRUCache, Node


class TestNode:
    def test_node_creation(self):
        node = Node("key1", "value1")
        assert node.key == "key1"
        assert node.value == "value1"
        assert node.prev_node is None
        assert node.next_node is None

    def test_node_str(self):
        node = Node("key1", "value1")
        assert str(node) == "Node: key1: value1"

    def test_node_attribute_changes(self):
        node = Node("k1", "v1")
        node.value = "new_value"
        node.key = "new_key"
        assert node.value == "new_value"
        assert node.key == "new_key"

    def test_node_links(self):
        node1 = Node("k1", "v1")
        node2 = Node("k2", "v2")
        node1.next_node = node2
        node2.prev_node = node1
        assert node1.next_node == node2
        assert node2.prev_node == node1


class TestLRUCache:
    def test_init_valid_limit(self):
        cache = LRUCache(5)
        assert cache.limit == 5
        assert len(cache.cache) == 0
        assert cache.head is None
        assert cache.tail is None

    def test_init_invalid_limit(self):
        with pytest.raises(ValueError, match="Limit должен быть больше 0"):
            LRUCache(0)
        with pytest.raises(ValueError, match="Limit должен быть больше 0"):
            LRUCache(-1)

    def test_add_first_node(self):
        cache = LRUCache(2)
        node = Node("k1", "v1")

        cache.add_node(node)

        assert cache.head == node
        assert cache.tail == node
        assert node.prev_node is None
        assert node.next_node is None

    def test_add_second_node(self):
        cache = LRUCache(2)
        node1 = Node("k1", "v1")
        node2 = Node("k2", "v2")

        cache.add_node(node1)
        cache.add_node(node2)

        assert cache.head == node2
        assert cache.tail == node1
        assert node2.next_node == node1
        assert node1.prev_node == node2
        assert node2.prev_node is None
        assert node1.next_node is None

    def test_sequential_inserts(self):
        cache = LRUCache(3)
        for i in range(3):
            cache.set(f"k{i}", f"v{i}")
        assert len(cache.cache) == 3
        assert cache.head.value == "v2"
        assert cache.tail.value == "v0"

    def test_cache_overflow(self):
        cache = LRUCache(2)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        assert len(cache.cache) == 2
        assert "k1" not in cache.cache
        assert "k3" in cache.cache

    def test_reuse_items(self):
        cache = LRUCache(3)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.get("k1")
        cache.set("k4", "v4")
        assert "k2" not in cache.cache
        assert "k1" in cache.cache

    def test_edge_cases(self):
        cache = LRUCache(1)
        cache.set("k1", "v1")
        assert cache.get("k1") == "v1"
        cache.set("k2", "v2")
        assert cache.get("k1") is None
        assert cache.get("k2") == "v2"

    def test_performance(self):
        cache = LRUCache(1000)
        start = time.time()
        for i in range(1000):
            cache.set(f"k{i}", f"v{i}")
        for i in range(1000):
            cache.get(f"k{i}")
        duration = time.time() - start
        assert duration < 1.0

    def test_complex_operations(self):
        cache = LRUCache(3)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.get("k1")
        cache.set("k3", "v3")
        cache.get("k2")
        cache.set("k4", "v4")

        assert sorted(cache.cache.keys()) == sorted(["k2", "k3", "k4"])
        assert cache.head.value == "v4"
        assert cache.tail.value == "v3"

    def test_none_values(self):
        cache = LRUCache(2)
        cache.set("k1", None)
        assert cache.get("k1") is None
        cache.set(None, "v2")
        assert cache.get(None) == "v2"

    def test_str_empty_cache(self):
        cache = LRUCache(2)
        assert str(cache) == ""

    def test_remove_only_node(self):
        cache = LRUCache(1)
        node = Node("k1", "v1")
        cache.add_node(node)

        cache.remove_node(node)

        assert cache.head is None
        assert cache.tail is None

    def test_remove_head_node(self):
        cache = LRUCache(2)
        node1 = Node("k1", "v1")
        node2 = Node("k2", "v2")
        cache.add_node(node1)
        cache.add_node(node2)

        cache.remove_node(node2)

        assert cache.head == node1
        assert cache.tail == node1
        assert node1.prev_node is None
        assert node1.next_node is None

    def test_remove_tail_node(self):
        cache = LRUCache(2)
        node1 = Node("k1", "v1")
        node2 = Node("k2", "v2")
        cache.add_node(node1)
        cache.add_node(node2)

        cache.remove_node(node1)

        assert cache.head == node2
        assert cache.tail == node2
        assert node2.prev_node is None
        assert node2.next_node is None

    def test_move_to_head(self):
        cache = LRUCache(3)
        node1 = Node("k1", "v1")
        node2 = Node("k2", "v2")
        node3 = Node("k3", "v3")
        cache.add_node(node1)
        cache.add_node(node2)
        cache.add_node(node3)

        cache.move_to_head(node2)

        assert cache.head == node2
        assert cache.tail == node1
        assert node2.next_node == node3
        assert node3.prev_node == node2
        assert node3.next_node == node1
        assert node1.prev_node == node3

    def test_pop_tail(self):
        cache = LRUCache(3)
        node1 = Node("k1", "v1")
        node2 = Node("k2", "v2")
        node3 = Node("k3", "v3")
        cache.add_node(node1)
        cache.add_node(node2)
        cache.add_node(node3)

        tail = cache.pop_tail()

        assert tail == node1
        assert cache.tail == node2
        assert node2.next_node is None
        assert "k1" not in cache.cache

    def test_get_existing_key(self):
        cache = LRUCache(2)
        cache.set("k1", "v1")
        cache.set("k2", "v2")

        with patch.object(cache, 'move_to_head') as mock_move:
            result = cache.get("k1")

            assert result == "v1"
            mock_move.assert_called_once()

    def test_get_non_existing_key(self):
        cache = LRUCache(2)
        assert cache.get("k3") is None

    def test_set_new_key(self):
        cache = LRUCache(2)
        with patch.object(cache, 'add_node') as mock_add:
            cache.set("k1", "v1")

            assert "k1" in cache.cache
            mock_add.assert_called_once()

    def test_set_existing_key(self):
        cache = LRUCache(2)
        cache.set("k1", "v1")

        with patch.object(cache, 'move_to_head') as mock_move:
            cache.set("k1", "v2")

            assert cache.cache["k1"].value == "v2"
            mock_move.assert_called_once()

    def test_set_evict_oldest(self):
        cache = LRUCache(2)
        cache.set("k1", "v1")
        cache.set("k2", "v2")

        test_node = Node("k1", "v1")
        with patch.object(cache, 'pop_tail', return_value=test_node):
            cache.set("k3", "v3")

            assert "k1" not in cache.cache
            assert "k3" in cache.cache

    def test_dict_interface(self):
        cache = LRUCache(2)
        cache["k1"] = "v1"
        assert cache["k1"] == "v1"
        assert cache["k2"] is None

    def test_str_representation(self):
        cache = LRUCache(2)
        cache.set("k1", "v1")
        cache.set("k2", "v2")

        result = str(cache)
        assert "Node: k1: v1" in result
        assert "Node: k2: v2" in result

    def test_lru_behavior_via_get_set(self):
        cache = LRUCache(3)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")

        cache.get("k1")

        cache.set("k4", "v4")

        assert cache.get("k1") == "v1"
        assert cache.get("k2") is None
        assert cache.get("k3") == "v3"
        assert cache.get("k4") == "v4"

    def test_constant_time_operations(self):
        cache = LRUCache(1000)

        start_insert = time.time()
        for i in range(1000):
            cache.set(f"k{i}", f"v{i}")
        insert_duration = time.time() - start_insert

        start_access = time.time()
        for i in range(1000):
            cache.get(f"k{i}")
        access_duration = time.time() - start_access

        start_evict = time.time()
        for i in range(1000, 2000):
            cache.set(f"k{i}", f"v{i}")
        evict_duration = time.time() - start_evict

        assert insert_duration < 0.1
        assert access_duration < 0.1
        assert evict_duration < 0.1

    def test_update_existing_key_and_lru(self):
        cache = LRUCache(3)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")

        cache.set("k2", "v2_updated")

        cache.set("k4", "v4")

        assert cache.get("k1") is None
        assert cache.get("k2") == "v2_updated"
        assert cache.get("k3") == "v3"
        assert cache.get("k4") == "v4"

    def test_lru_example_from_task(self):
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
