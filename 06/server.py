import argparse
import json
import re
import socket
import threading
from collections import Counter
from queue import Queue
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class Worker(threading.Thread):
    def __init__(self, worker_id, task_queue, result_queue, k, stop_event):
        super().__init__()
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.k = k
        self.stop_event = stop_event
        self.daemon = True
        self.timeout = 10
        self.max_content_length = 2 * 1024 * 1024
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'text/html'
        }

    def run(self):
        while not self.stop_event.is_set():
            try:
                client_socket, url = self.task_queue.get(timeout=1)
                processed = 0
                try:
                    if not self.is_valid_url(url):
                        raise ValueError(f"Invalid URL format: {url}")

                    req = Request(url, headers=self.headers)
                    with urlopen(req, timeout=self.timeout) as response:
                        if response.status != 200:
                            raise HTTPError(url, response.status, "HTTP Error", response.headers, None)

                        content_length = int(response.headers.get('Content-Length', 0))
                        if content_length > self.max_content_length:
                            raise ValueError(f"Content too large: {content_length} bytes")

                        html = response.read(self.max_content_length).decode('utf-8', errors='ignore')
                        words = re.findall(r'\w+', html.lower())
                        word_counts = Counter(words)
                        top_words = dict(word_counts.most_common(self.k))

                        result = {
                            'url': url,
                            'result': top_words,
                            'status': 'success'
                        }
                        processed = 1
                except Exception as e:
                    result = {
                        'url': url,
                        'error': str(e),
                        'status': 'error'
                    }
                finally:
                    try:
                        client_socket.sendall(json.dumps(result).encode('utf-8'))
                        client_socket.close()
                    except Exception as e:
                        print(f"Failed to send response for {url}: {e}")
                    self.result_queue.put(processed)
                    self.task_queue.task_done()
            except Exception:
                continue

    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False


class Master:
    def __init__(self, host, port, num_workers, k):
        self.host = host
        self.port = port
        self.num_workers = num_workers
        self.k = k
        self.task_queue = Queue(maxsize=100)
        self.result_queue = Queue()
        self.stop_event = threading.Event()
        self.workers = []
        self.stats_thread = None
        self.server_socket = None
        self.lock = threading.Lock()
        self.processed_count = 0

    def start_statistics_thread(self):
        def print_statistics():
            while not self.stop_event.is_set():
                try:
                    count = self.result_queue.get(timeout=1)
                    with self.lock:
                        self.processed_count += count
                        print(f"Total URLs processed: {self.processed_count}")
                except Exception:
                    continue

        self.stats_thread = threading.Thread(target=print_statistics, daemon=True)
        self.stats_thread.start()

    def start_workers(self):
        for i in range(self.num_workers):
            worker = Worker(i, self.task_queue, self.result_queue, self.k, self.stop_event)
            worker.start()
            self.workers.append(worker)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.settimeout(1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Server listening on {self.host}:{self.port} with {self.num_workers} workers")

        try:
            while not self.stop_event.is_set():
                try:
                    conn, _ = self.server_socket.accept()
                    conn.settimeout(5)

                    try:
                        data = conn.recv(4096)
                        if not data:
                            conn.close()
                            continue

                        with self.lock:
                            if self.task_queue.full():
                                response = json.dumps({
                                    'error': 'Server busy',
                                    'status': 'retry'
                                }).encode('utf-8')
                                conn.sendall(response)
                                conn.close()
                                print("Queue full - request rejected")
                                continue

                            self.task_queue.put((conn, data))
                            print(f"Request accepted: {data.decode()[:100]}...")

                    except Exception as e:
                        print(f"Client handling error: {e}")
                        try:
                            conn.close()
                        except Exception:
                            pass

                except socket.timeout:
                    continue

        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.shutdown()

    def shutdown(self):
        print("Shutting down server...")
        self.stop_event.set()

        if self.server_socket:
            self.server_socket.close()

        for worker in self.workers:
            worker.join(timeout=1)

        if self.stats_thread:
            self.stats_thread.join(timeout=1)

        print(f"Final count: {self.processed_count} URLs processed")


def parse_args():
    parser = argparse.ArgumentParser(description='URL processing server')
    parser.add_argument('-w', '--workers', type=int, required=True,
                        help='Number of worker threads (recommend 5-10)')
    parser.add_argument('-k', type=int, required=True,
                        help='Number of top words to return')
    parser.add_argument('--host', default='localhost',
                        help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=5000,
                        help='Server port (default: 5000)')
    return parser.parse_args()


def main():
    args = parse_args()
    master = Master(args.host, args.port, args.workers, args.k)
    try:
        master.start_workers()
        master.start_statistics_thread()
        master.start_server()
    except KeyboardInterrupt:
        master.shutdown()
    except Exception as e:
        print(f"Fatal error: {e}")
        master.shutdown()


if __name__ == '__main__':
    main()
