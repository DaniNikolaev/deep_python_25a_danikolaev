import threading
from queue import Empty, Queue
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import pytest
from server import Master, Worker


class TestServer:
    @pytest.fixture
    def mock_worker(self):
        task_queue = Queue()
        result_queue = Queue()
        worker = Worker(0, task_queue, result_queue, 3)
        worker.daemon = True
        return worker

    @pytest.fixture
    def mock_master(self):
        return Master('localhost', 0, 3, 5)

    def test_worker_initialization(self, mock_worker):
        assert mock_worker.worker_id == 0
        assert mock_worker.k == 3
        assert mock_worker.daemon is True

    def test_master_initialization(self, mock_master):
        assert mock_master.host == 'localhost'
        assert mock_master.port == 0
        assert mock_master.num_workers == 3
        assert mock_master.k == 5

    @patch('urllib.request.urlopen')
    @patch('socket.socket')
    def test_worker_error_handling(self, mock_socket, mock_urlopen, mock_worker):
        mock_urlopen.side_effect = URLError("test error")
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        try:
            mock_worker.task_queue.put((mock_sock_instance, "http://invalid.com"), timeout=1.0)

            worker_thread = threading.Thread(target=mock_worker.run)
            worker_thread.daemon = True
            worker_thread.start()

            worker_thread.join(timeout=2.0)
            try:
                result = mock_worker.result_queue.get(timeout=1.0)
                assert result == 0
            except Empty:
                pytest.fail("Worker did not put result in queue within 1 second timeout")
        except Exception as e:
            print(f"Unexpected error in test: {e}")
            raise

    @patch('urllib.request.urlopen')
    def test_multiple_workers_processing(self, mock_urlopen):
        class MockResponse:
            def read(self):
                return b"word1 word2 word1"

            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        mock_urlopen.return_value = MockResponse()

        mock_worker1 = Worker(1, Queue(), Queue(), 3)
        mock_worker1.daemon = True
        mock_worker2 = Worker(2, Queue(), Queue(), 3)
        mock_worker2.daemon = True

        try:
            mock_worker1.task_queue.put((MagicMock(), "http://test1.com"), timeout=1.0)
            mock_worker2.task_queue.put((MagicMock(), "http://test2.com"), timeout=1.0)

            worker_thread1 = threading.Thread(target=mock_worker1.run)
            worker_thread1.daemon = True
            worker_thread2 = threading.Thread(target=mock_worker2.run)
            worker_thread2.daemon = True

            worker_thread1.start()
            worker_thread2.start()

            worker_thread1.join(timeout=2.0)
            worker_thread2.join(timeout=2.0)

            try:
                assert mock_worker1.result_queue.get(timeout=1.0) is not None
                assert mock_worker2.result_queue.get(timeout=1.0) is not None
            except Empty:
                pytest.fail("Workers did not produce results within timeout")

        except Exception as e:
            pytest.fail(f"Test failed with exception: {str(e)}")
