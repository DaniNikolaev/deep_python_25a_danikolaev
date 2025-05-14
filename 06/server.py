import argparse
import json
import re
import socket
import threading
from collections import Counter
from queue import Queue
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class Worker(threading.Thread):
    def __init__(self, worker_id, task_queue, result_queue, k):
        super().__init__()
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.k = k
        self.daemon = True

    def run(self):
        while True:
            client_socket, url = self.task_queue.get()
            try:
                with urlopen(url) as response:
                    html = response.read().decode('utf-8')
                    words = re.findall(r'\w+', html.lower())
                    word_counts = Counter(words)
                    top_words = dict(word_counts.most_common(self.k))

                result_json = json.dumps(top_words)
                with client_socket:
                    client_socket.sendall(result_json.encode('utf-8'))

                self.result_queue.put(1)
            except (URLError, HTTPError) as e:
                print(f"Error processing URL {url}: {e}")
                with client_socket:
                    client_socket.sendall(json.dumps({"error": str(e)}).encode('utf-8'))
                self.result_queue.put(0)


class Master:
    def __init__(self, host, port, num_workers, k):
        self.host = host
        self.port = port
        self.num_workers = num_workers
        self.k = k
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.total_processed = 0
        self.workers = []
        self.stats_thread = None

    def start_statistics_thread(self):
        def print_statistics():
            while True:
                count = self.result_queue.get()
                self.total_processed += count
                print(f"Total URLs processed: {self.total_processed}")

        self.stats_thread = threading.Thread(target=print_statistics, daemon=True)
        self.stats_thread.start()

    def start_workers(self):
        for i in range(self.num_workers):
            worker = Worker(i, self.task_queue, self.result_queue, self.k)
            worker.start()
            self.workers.append(worker)

    def run(self):
        self.start_workers()
        self.start_statistics_thread()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                print(f"Connected by {addr}")

                data = conn.recv(4096)
                if not data:
                    conn.close()
                    continue

                url = data.decode('utf-8').strip()
                print(f"Received URL: {url}")

                self.task_queue.put((conn, url))


def main():
    parser = argparse.ArgumentParser(description='URL processing server')
    parser.add_argument('-w', '--workers', type=int, required=True, help='Number of worker threads')
    parser.add_argument('-k', type=int, required=True, help='Number of top words to return')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=5000, help='Server port')

    args = parser.parse_args()

    master = Master(args.host, args.port, args.workers, args.k)
    master.run()


if __name__ == '__main__':
    main()
