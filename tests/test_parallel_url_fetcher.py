import pytest
from typing import NoReturn
from unittest.mock import patch, MagicMock
from uqload_dl.parallel_url_fetcher import ParallelURLFetcher


def test_valid_urls_fetch_success() -> None:
    urls = ["https://example.com/1", "https://example.com/2"]

    mock_response1 = MagicMock()
    mock_response1.getcode.return_value = 200
    mock_response1.read.return_value = b"content1"
    mock_response1.__enter__.return_value = mock_response1

    mock_response2 = MagicMock()
    mock_response2.getcode.return_value = 200
    mock_response2.read.return_value = b"content2"
    mock_response2.__enter__.return_value = mock_response2

    with patch("urllib.request.urlopen", side_effect=[mock_response1, mock_response2]):
        fetcher = ParallelURLFetcher(urls)
        result = fetcher.fetch_all()
        assert result == ["content1", "content2"]


def test_fetch_with_invalid_url_returns_none() -> None:
    urls = ["https://example.com/valid", "https://example.com/404"]

    mock_valid = MagicMock()
    mock_valid.getcode.return_value = 200
    mock_valid.read.return_value = b"ok"
    mock_valid.__enter__.return_value = mock_valid

    mock_invalid = MagicMock()
    mock_invalid.getcode.return_value = 404
    mock_invalid.__enter__.return_value = mock_invalid

    with patch("urllib.request.urlopen", side_effect=[mock_valid, mock_invalid]):
        fetcher = ParallelURLFetcher(urls)
        result = fetcher.fetch_all()
        assert result == ["ok", None]


def test_fetch_with_exception_returns_none() -> None:
    urls = ["https://example.com/valid", "https://example.com/error"]

    mock_valid = MagicMock()
    mock_valid.getcode.return_value = 200
    mock_valid.read.return_value = b"success"
    mock_valid.__enter__.return_value = mock_valid

    def raise_error(*args, **kwargs) -> NoReturn:
        raise Exception("Network error")

    with patch("urllib.request.urlopen", side_effect=[mock_valid, raise_error]):
        fetcher = ParallelURLFetcher(urls)
        result = fetcher.fetch_all()
        assert result == ["success", None]


def test_invalid_urls_raise_value_error():
    with pytest.raises(ValueError):
        ParallelURLFetcher([])

    with pytest.raises(ValueError):
        ParallelURLFetcher(["", None])
