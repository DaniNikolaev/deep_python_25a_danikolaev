import json
import socket
import threading
import unittest
from io import StringIO
from queue import Queue
from unittest.mock import MagicMock, patch

from client import URLProcessor, URLReader, start_processing


class TestURLProcessor(unittest.TestCase):
    def setUp(self):
        self.url_queue = Queue()
        self.stop_event = threading.Event()
        self.processor = URLProcessor(self.url_queue, 'localhost', 5000, self.stop_event)

    @patch('client.socket.socket')
    def test_process_url_success(self, mock_socket):
        mock_conn = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_conn

        test_url = "http://example.com"
        expected_result = {'status': 'success', 'result': 'test result'}
        mock_conn.recv.return_value = json.dumps(expected_result).encode('utf-8')

        result = self.processor.process_url(test_url)
        self.assertTrue(result)
        mock_conn.sendall.assert_called_once_with(test_url.encode('utf-8'))

    @patch('client.socket.socket')
    def test_process_url_retry(self, mock_socket):
        mock_conn = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_conn

        mock_conn.recv.return_value = json.dumps({'status': 'retry'}).encode('utf-8')
        result = self.processor.process_url("http://example.com")
        self.assertFalse(result)

    @patch('client.socket.socket')
    def test_process_url_timeout(self, mock_socket):
        mock_socket.return_value.__enter__.side_effect = socket.timeout()
        result = self.processor.process_url("http://example.com")
        self.assertFalse(result)


class TestURLReader(unittest.TestCase):
    def test_url_reader(self):
        url_queue = Queue()
        stop_event = threading.Event()
        test_urls = ["http://test1.com", "http://test2.com"]

        with patch('builtins.open', return_value=StringIO("\n".join(test_urls))):
            reader = URLReader("dummy.txt", url_queue, stop_event)
            reader.start()
            reader.join()

        queued_urls = []
        while not url_queue.empty():
            queued_urls.append(url_queue.get())

        self.assertEqual(set(queued_urls), set(test_urls))


class TestClientIntegration(unittest.TestCase):
    @patch('client.URLReader')
    @patch('client.URLProcessor')
    @patch('client.Queue')
    def test_start_processing(self, mock_queue, mock_processor, mock_reader):
        mock_queue_instance = MagicMock()
        mock_queue.return_value = mock_queue_instance

        mock_reader_instance = MagicMock()
        mock_reader.return_value = mock_reader_instance

        mock_processor.side_effect = [MagicMock() for _ in range(3)]

        args = MagicMock()
        args.threads = 3
        args.url_file = "test.txt"
        args.host = "localhost"
        args.port = 5000

        with patch('client.threading.Event', return_value=MagicMock()):
            start_processing(args)

        self.assertEqual(mock_processor.call_count, 3)
        mock_reader_instance.start.assert_called_once()


if __name__ == '__main__':
    unittest.main()
