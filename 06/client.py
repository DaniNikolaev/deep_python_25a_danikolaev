import argparse
import json
import socket
import threading


class URLProcessor(threading.Thread):
    def __init__(self, urls, host, port):
        super().__init__()
        self.urls = urls
        self.host = host
        self.port = port

    def run(self):
        for url in self.urls:
            url = url.strip()
            if not url:
                continue

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    s.sendall(url.encode('utf-8'))

                    data = s.recv(4096)
                    result = json.loads(data.decode('utf-8'))
                    print(f"{url}: {result}")
            except (socket.error, json.JSONDecodeError) as e:
                print(f"Error processing {url}: {e}")


def main():
    parser = argparse.ArgumentParser(description='URL processing client')
    parser.add_argument('threads', type=int, help='Number of threads')
    parser.add_argument('url_file', help='File containing URLs')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=5000, help='Server port')

    args = parser.parse_args()

    try:
        with open(args.url_file, 'r', encoding='utf-8') as f:
            urls = f.readlines()
    except IOError as e:
        print(f"Error reading URL file: {e}")
        return

    chunk_size = len(urls) // args.threads
    threads = []

    for i in range(args.threads):
        start = i * chunk_size
        end = None if i == args.threads - 1 else start + chunk_size
        thread_urls = urls[start:end]

        processor = URLProcessor(thread_urls, args.host, args.port)
        threads.append(processor)
        processor.start()

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
