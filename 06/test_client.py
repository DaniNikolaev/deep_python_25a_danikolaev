import json
import socket
from unittest.mock import MagicMock, patch

import pytest
from client import URLProcessor, main


class TestClient:
    @pytest.fixture
    def mock_processor(self):
        return URLProcessor(["http://test.com"], "localhost", 5000)

    def test_url_processor_initialization(self, mock_processor):
        assert mock_processor.urls == ["http://test.com"]
        assert mock_processor.host == "localhost"
        assert mock_processor.port == 5000

    @patch('socket.socket')
    def test_url_processor_success(self, mock_socket, mock_processor, capsys):
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        mock_response = json.dumps({"test": 3}).encode('utf-8')
        mock_sock_instance.recv.return_value = mock_response

        mock_processor.run()

        captured = capsys.readouterr()
        assert "http://test.com: {'test': 3}" in captured.out
        mock_sock_instance.connect.assert_called_once_with(("localhost", 5000))
        mock_sock_instance.sendall.assert_called_once_with(b"http://test.com")

    @patch('socket.socket')
    def test_url_processor_socket_error(self, mock_socket, mock_processor, capsys):
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        mock_sock_instance.connect.side_effect = socket.error("connection failed")

        mock_processor.run()

        captured = capsys.readouterr()
        assert "Error processing http://test.com: connection failed" in captured.out

    @patch('builtins.open')
    @patch('client.URLProcessor')
    def test_main_file_handling(self, mock_processor, mock_open):
        mock_file = MagicMock()
        mock_file.__enter__.return_value.readlines.return_value = [
            "http://test1.com\n",
            "http://test2.com\n",
            "http://test3.com\n",
            "http://test4.com\n"
        ]
        mock_open.return_value = mock_file

        created_threads = []

        class MockThread:
            def __init__(self, target=None, args=()):
                self.target = target
                self.args = args
                created_threads.append(self)

            def start(self):
                if self.target:
                    self.target(*self.args)

            def join(self):
                pass

        test_args = ["client.py", "2", "test_urls.txt"]

        with patch('sys.argv', test_args):
            with patch('threading.Thread', MockThread):
                processor_creations = []

                def processor_side_effect(urls, host, port):
                    mock = MagicMock()
                    processor_creations.append(([url.strip() for url in urls], host, port))
                    return mock

                mock_processor.side_effect = processor_side_effect

                main()

                mock_open.assert_called_once_with("test_urls.txt", 'r', encoding='utf-8')

                assert len(processor_creations) == 2

                expected_chunk1 = ["http://test1.com", "http://test2.com"]
                expected_chunk2 = ["http://test3.com", "http://test4.com"]
                assert ((processor_creations[0][0] == expected_chunk1
                        and processor_creations[1][0] == expected_chunk2)
                        or (processor_creations[0][0] == expected_chunk2
                        and processor_creations[1][0] == expected_chunk1))

                assert all(hasattr(t, 'target') for t in created_threads)

    @patch('builtins.open')
    def test_main_file_error(self, mock_open, capsys):
        mock_open.side_effect = IOError("file error")

        test_args = ["client.py", "2", "test_urls.txt"]

        with patch('sys.argv', test_args):
            main()

            captured = capsys.readouterr()
            assert "Error reading URL file: file error" in captured.out
