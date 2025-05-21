# pylint: disable=redefined-outer-name
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fetcher import URLFetcher, main


@pytest.fixture
def mock_client_response():
    response = AsyncMock()
    response.status = 200
    response.text = AsyncMock(return_value="test content")
    return response


@pytest.fixture
def fetcher():
    return URLFetcher(concurrency=2)


@pytest.mark.asyncio
async def test_fetch_url_success(fetcher):
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.text = AsyncMock(return_value="test content")

    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_context_manager)

    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value = mock_context_manager()

        fetcher = URLFetcher()
        fetcher.session = mock_session
        result = await fetcher.fetch_url("http://example.com")
        assert result == {
            "url": "http://example.com",
            "status": 200,
            "content": "test content"
        }


@pytest.mark.asyncio
async def test_fetch_url_timeout(fetcher):
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = Exception("Timeout (5s)")
        fetcher = URLFetcher()
        result = await fetcher.fetch_url("http://example.com")
        assert result == {
            "url": "http://example.com",
            "error": "Timeout (5s)"
        }


@pytest.mark.asyncio
async def test_fetch_url_other_error(fetcher):
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        fetcher = URLFetcher()
        result = await fetcher.fetch_url("http://example.com")
        assert result == {
            "url": "http://example.com",
            "error": "Connection error"
        }


@pytest.mark.asyncio
async def test_fetch_urls_concurrency(fetcher, mock_client_response):
    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_client_response)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        urls = [f"http://example.com/{i}" for i in range(5)]
        results = await fetcher.fetch_urls(urls)

        assert len(results) == 5
        assert mock_session.get.call_count == 5


@pytest.mark.asyncio
async def test_fetch_urls_semaphore(fetcher):
    request_times = []

    async def mock_get(url):
        st = time.time()
        await asyncio.sleep(0.1)
        en = time.time()
        request_times.append((st, en))

        response = AsyncMock()
        response.status = 200
        response.text.return_value = "content"
        return response

    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()
    mock_session.get = AsyncMock(side_effect=mock_get)

    with patch('aiohttp.ClientSession', return_value=mock_session):
        urls = [f"http://example.com/{i}" for i in range(5000)]
        start_time = time.time()
        await fetcher.fetch_urls(urls)
        total_time = time.time() - start_time

        assert 0.25 <= total_time < 0.4

        max_concurrent = 0
        timeline = []
        for start, end in request_times:
            timeline.append((start, 1))
            timeline.append((end, -1))

        timeline.sort()
        current = 0
        for delta in timeline:
            current += delta[1]
            max_concurrent = max(max_concurrent, current)

        assert max_concurrent <= fetcher.concurrency


@pytest.mark.asyncio
async def test_close_session(fetcher, mock_client_response):
    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock()
    mock_session.get = AsyncMock(return_value=mock_client_response)
    mock_session.close = AsyncMock()

    with patch('aiohttp.ClientSession', return_value=mock_session):
        await fetcher.fetch_url("http://example.com")
        await fetcher.close()

        mock_session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_without_session(fetcher):
    await fetcher.close()


@pytest.mark.asyncio
async def test_main_with_file(tmp_path):
    url_file = tmp_path / "urls.txt"
    url_file.write_text("http://example.com/1\nhttp://example.com/2\n")

    mock_results = [
        {"url": "http://example.com/1", "status": 200, "content": "test1"},
        {"url": "http://example.com/2", "status": 200, "content": "test2"}
    ]

    mock_fetcher = AsyncMock()
    mock_fetcher.fetch_urls.return_value = mock_results
    mock_fetcher.close = AsyncMock()

    with patch('fetcher.URLFetcher', return_value=mock_fetcher) as mock_fetcher_class:
        await main(2, str(url_file))

        mock_fetcher_class.assert_called_once_with(concurrency=2)
        mock_fetcher.fetch_urls.assert_awaited_once()
        mock_fetcher.close.assert_awaited_once()
