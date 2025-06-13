import argparse
import json
import socket
import threading
import time
from queue import Queue


class URLProcessor(threading.Thread):
    def __init__(self, url_queue, host, port, stop_event):
        super().__init__()
        self.url_queue = url_queue
        self.host = host
        self.port = port
        self.stop_event = stop_event
        self.timeout = 15
        self.retry_delay = 5

    def process_url(self, url):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                s.connect((self.host, self.port))
                s.sendall(url.encode('utf-8'))

                data = s.recv(4096)
                result = json.loads(data.decode('utf-8'))

                if result.get('status') == 'retry':
                    print(f"Server busy, will retry: {url}")
                    time.sleep(self.retry_delay)
                    return False

                print(f"{url}: {result.get('result', result.get('error'))}")
                return True

        except (socket.timeout, ConnectionRefusedError):
            print(f"Connection error, will retry: {url}")
            time.sleep(self.retry_delay)
            return False
        except json.JSONDecodeError:
            print(f"Invalid response for {url}")
            return True
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return True

    def run(self):
        while not self.stop_event.is_set():
            url = self.url_queue.get()
            if url is None:
                self.url_queue.task_done()
                break

            success = self.process_url(url)
            if not success:
                self.url_queue.put(url)

            self.url_queue.task_done()


class URLReader(threading.Thread):
    def __init__(self, url_file, url_queue, stop_event):
        super().__init__()
        self.url_file = url_file
        self.url_queue = url_queue
        self.stop_event = stop_event
        self.daemon = True

    def run(self):
        try:
            with open(self.url_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if self.stop_event.is_set():
                        break
                    url = line.strip()
                    if url:
                        self.url_queue.put(url)
        except IOError as e:
            print(f"Error reading URL file: {e}")


def start_processing(arg_s):
    stop_event = threading.Event()
    url_queue = Queue(maxsize=20)
    threads = []

    reader = URLReader(arg_s.url_file, url_queue, stop_event)
    reader.start()

    for _ in range(arg_s.threads):
        processor = URLProcessor(url_queue, arg_s.host, arg_s.port, stop_event)
        processor.start()
        threads.append(processor)

    try:
        reader.join()

        for _ in range(arg_s.threads):
            url_queue.put(None)

        url_queue.join()

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        stop_event.set()

        while not url_queue.empty():
            url_queue.get()
            url_queue.task_done()

    finally:
        for thread in threads:
            thread.join()


def parse_args():
    parser = argparse.ArgumentParser(description='URL processing client')
    parser.add_argument('threads', type=int, help='Number of processing threads')
    parser.add_argument('url_file', help='File containing URLs (one per line)')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    start_processing(args)
