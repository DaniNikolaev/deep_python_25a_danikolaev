import os
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
        return Worker(0, task_queue, result_queue, 3)

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

    @pytest.mark.skipif(os.getenv('CI') == 'true', reason="Flaky in CI")
    @patch('urllib.request.urlopen')
    def test_worker_error_handling(self, mock_urlopen, mock_worker):
        mock_urlopen.side_effect = URLError("test error")

        mock_socket = MagicMock()
        mock_worker.task_queue.put((mock_socket, "http://invalid.com"))

        worker_thread = threading.Thread(target=mock_worker.run)
        worker_thread.start()
        worker_thread.join(timeout=1)

        try:
            result = mock_worker.result_queue.get(timeout=0.1)
            assert result == 0
        except Empty:
            pytest.fail("Worker did not put result in queue within the timeout")

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
        mock_worker2 = Worker(2, Queue(), Queue(), 3)

        mock_worker1.task_queue.put((MagicMock(), "http://test1.com"))
        mock_worker2.task_queue.put((MagicMock(), "http://test2.com"))

        worker_thread1 = threading.Thread(target=mock_worker1.run)
        worker_thread2 = threading.Thread(target=mock_worker2.run)

        worker_thread1.start()
        worker_thread2.start()

        worker_thread1.join(timeout=1)
        worker_thread2.join(timeout=1)

        assert mock_worker1.result_queue.qsize() == 1
        assert mock_worker2.result_queue.qsize() == 1
