import json
import queue
import socket
import threading
import time
from queue import Queue
from unittest.mock import MagicMock, patch

import pytest
from server import Master, Worker


@pytest.fixture
def worker_setup():
    task_queue = Queue()
    result_queue = Queue()
    stop_event = threading.Event()
    worker = Worker(
        worker_id=1,
        task_queue=task_queue,
        result_queue=result_queue,
        k=3,
        stop_event=stop_event
    )
    return worker, task_queue, result_queue, stop_event


@pytest.fixture
def master_setup():
    with patch('server.socket.socket'):
        master = Master('localhost', 5000, 3, 5)
        master.server_socket = MagicMock()
        yield master


class TestWorker:
    def test_process_valid_url(self, worker_setup):
        worker, task_queue, result_queue, _ = worker_setup

        mock_client = MagicMock()
        task_queue.put((mock_client, "http://example.com"))

        with patch('server.urlopen') as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.status = 200
            mock_resp.headers = {'Content-Length': '100'}
            mock_resp.read.return_value = b'<html>test test example</html>'
            mock_urlopen.return_value.__enter__.return_value = mock_resp

            def run_worker():
                worker.run()

            t = threading.Thread(target=run_worker)
            t.start()

            time.sleep(0.1)
            worker.stop_event.set()
            t.join(timeout=1)

            mock_client.sendall.assert_called_once()
            assert result_queue.qsize() == 1
            assert result_queue.get() == 1

    def test_process_invalid_url(self, worker_setup):
        worker, task_queue, _, _ = worker_setup

        mock_client = MagicMock()
        task_queue.put((mock_client, "invalid_url"))

        def run_worker():
            worker.run()

        t = threading.Thread(target=run_worker)
        t.start()

        time.sleep(0.1)
        worker.stop_event.set()
        t.join(timeout=1)

        mock_client.sendall.assert_called_once()
        sent_data = json.loads(mock_client.sendall.call_args[0][0].decode())
        assert sent_data['status'] == 'error'


class TestMaster:
    def test_start_workers(self, master_setup):
        master = master_setup
        master.start_workers()
        assert len(master.workers) == 3
        for worker in master.workers:
            assert worker.is_alive()


class TestIntegration:
    @patch('server.urlopen')
    @patch('server.socket.socket')
    def test_full_workflow(self, mock_socket, mock_urlopen):
        mock_server = MagicMock()
        mock_socket.return_value = mock_server

        mock_client = MagicMock()
        mock_client.recv.return_value = b'http://example.com'

        mock_server.accept.side_effect = [
            (mock_client, ('127.0.0.1', 12345)),
            socket.timeout()
        ]

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'<html>test content</html>'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        master = Master('localhost', 5000, 3, 5)
        master.task_queue = queue.Queue()
        master.result_queue = queue.Queue()

        master.start_workers()

        server_thread = threading.Thread(target=master.start_server)
        server_thread.start()

        time.sleep(0.1)

        master.task_queue.put((mock_client, 'http://example.com'))

        time.sleep(0.1)

        assert mock_client.sendall.called, "sendall was not called"
        sent_data = json.loads(mock_client.sendall.call_args[0][0].decode())
        assert sent_data['status'] == 'success'
