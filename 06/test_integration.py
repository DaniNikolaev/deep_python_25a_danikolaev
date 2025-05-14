import socket
import threading
import time
from unittest.mock import patch
from urllib.error import URLError

import pytest
from client import URLProcessor
from server import Master


class TestIntegration:
    @pytest.fixture
    def start_test_server(self):
        master = Master('localhost', 5001, 2, 3)
        server_thread = threading.Thread(target=master.run)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.1)
        yield master

    def test_client_server_communication(self, start_test_server):
        test_urls = ["http://example.com", "http://python.org"]

        processor = URLProcessor(test_urls, "localhost", 5001)
        processor_thread = threading.Thread(target=processor.run)
        processor_thread.start()
        processor_thread.join(timeout=2)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            assert s.connect_ex(('localhost', 5001)) == 0

    @patch('urllib.request.urlopen')
    def test_server_processes_urls(self, mock_urlopen, start_test_server):
        class MockResponse:
            def read(self):
                return b"word1 word2 word1 word3 word2 word1"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        mock_urlopen.return_value = MockResponse()

        test_urls = ["http://example.com"]
        processor = URLProcessor(test_urls, "localhost", 5001)
        processor_thread = threading.Thread(target=processor.run)
        processor_thread.start()
        processor_thread.join(timeout=2)

    @patch('urllib.request.urlopen')
    def test_server_handles_invalid_url(self, mock_urlopen, start_test_server):
        mock_urlopen.side_effect = URLError("Invalid URL")

        test_urls = ["http://invalid-url.com"]
        processor = URLProcessor(test_urls, "localhost", 5001)
        processor_thread = threading.Thread(target=processor.run)
        processor_thread.start()
        processor_thread.join(timeout=2)

    def test_statistics(self, start_test_server):
        test_urls = ["http://example.com"]
        processor = URLProcessor(test_urls, "localhost", 5001)
        processor_thread = threading.Thread(target=processor.run)
        processor_thread.start()
        processor_thread.join(timeout=2)
