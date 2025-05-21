# pylint: disable=import-error
import argparse
import asyncio
import time

import aiohttp


class URLFetcher:
    def __init__(self, concurrency=5):
        self.concurrency = concurrency
        self.session = None

    async def fetch_url(self, url):
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=5, connect=2)
            self.session = aiohttp.ClientSession(timeout=timeout)
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                return {
                    "url": url,
                    "status": response.status,
                    "content": content[:100]
                }
        except asyncio.TimeoutError:
            return {"url": url, "error": "Timeout (5s)"}
        except Exception as e:
            return {"url": url, "error": str(e)}

    async def fetch_urls(self, urls):
        semaphore = asyncio.Semaphore(self.concurrency)

        async def fetch_with_semaphore(url: str):
            async with semaphore:
                return await self.fetch_url(url)

        tasks = [fetch_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks)

    async def close(self):
        if self.session:
            await self.session.close()


async def main(concurrency, input_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    fetcher = URLFetcher(concurrency=concurrency)

    try:
        start_time = time.time()
        results = await fetcher.fetch_urls(urls)
        elapsed = time.time() - start_time

        for result in results:
            if "error" in result:
                print(f"Ошибка {result['url']}: {result['error']}")
            else:
                print(f"Извлечен {result['url']} (status: {result['status']})")

        print(f"\nИзвлечено {len(results)} URLs за {elapsed:.2f} секунд")
        print(f"Уровень параллельности: {concurrency}")
    finally:
        await fetcher.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async URL fetcher")
    parser.add_argument("concurrency", type=int, help="Number of concurrent requests")
    parser.add_argument("input_file", help="File containing URLs (one per line)")
    args = parser.parse_args()

    asyncio.run(main(args.concurrency, args.input_file))
