import os
import pytest
from unittest.mock import patch, MagicMock
from uqload_dl.file_downloader import FileDownloader
from typing import Dict


@pytest.fixture
def test_data() -> Dict[str, str]:
    return {
        "url": "https://example.com/test_file.txt",
        "filename": "custom_name",
        "output_dir": os.path.dirname(__file__),
    }


@patch("uqload_dl.file_downloader.urllib.request.urlopen")
def test_valid_url_and_metadata(mock_urlopen, test_data: Dict[str, str]) -> None:
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.info.return_value = {
        "Content-Length": "100",
        "Content-Type": "text/plain",
    }
    mock_urlopen.return_value.__enter__.return_value = mock_response

    downloader = FileDownloader(url=test_data["url"])
    assert downloader.url == test_data["url"]
    assert downloader.total_size == 100
    assert downloader.type == "text/plain"


def test_invalid_url() -> None:
    with pytest.raises(ValueError):
        FileDownloader("invalid_url.txt")


@patch("uqload_dl.file_downloader.urllib.request.urlopen")
def test_callback_validation(mock_urlopen, test_data: Dict[str, str]) -> None:
    def callback(downloaded, total) -> None:
        pass

    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.__enter__.return_value = mock_response

    mock_urlopen.return_value = mock_response

    downloader = FileDownloader(url=test_data["url"], on_progress_callback=callback)
    assert downloader.on_progress_callback == callback

    with pytest.raises(ValueError):
        FileDownloader(url=test_data["url"], on_progress_callback="not_callable")


@patch("uqload_dl.file_downloader.urllib.request.urlopen")
def test_download_creates_file(mock_urlopen, test_data: Dict[str, str]) -> None:
    mock_head_response = MagicMock()
    mock_head_response.getcode.return_value = 200
    mock_head_response.info.return_value = {
        "Content-Length": "16",
        "Content-Type": "text/plain",
    }

    mock_download_response = MagicMock()
    mock_download_response.getcode.return_value = 200
    mock_download_response.read.side_effect = [b"Hello, world!\n", b""]

    mock_head_response.__enter__.return_value = mock_head_response
    mock_download_response.__enter__.return_value = mock_download_response

    mock_urlopen.side_effect = [mock_head_response, mock_download_response]

    downloader = FileDownloader(
        test_data["url"], filename="testfile", output_dir=test_data["output_dir"]
    )
    downloader.download()

    assert os.path.isfile(downloader.destination)

    downloader.delete_file()
    assert not os.path.isfile(downloader.destination)


@patch("uqload_dl.file_downloader.urllib.request.urlopen")
def test_download_keyboard_interrupt(mock_urlopen, test_data: Dict[str, str]) -> None:
    mock_response = MagicMock()
    mock_response.getcode.return_value = 200
    mock_response.read.side_effect = KeyboardInterrupt()

    mock_response.__enter__.return_value = mock_response

    mock_urlopen.side_effect = [mock_response, mock_response]

    downloader = FileDownloader(
        test_data["url"], filename="testfile", output_dir=test_data["output_dir"]
    )

    try:
        downloader.download()
    except KeyboardInterrupt:
        pytest.fail("Download should handle KeyboardInterrupt internally")
    finally:
        downloader.delete_file()


@patch("uqload_dl.file_downloader.urllib.request.urlopen")
def test_download_raises_on_404_and_does_not_create_file(
    mock_urlopen, test_data: Dict[str, str]
) -> None:
    mock_response = MagicMock()
    mock_response.getcode.return_value = 404
    mock_response.__enter__.return_value = mock_response

    mock_urlopen.return_value = mock_response

    with pytest.raises(ValueError) as exc_info:
        downloader = FileDownloader(
            test_data["url"], output_dir=test_data["output_dir"]
        )
        downloader.download()

    assert "non-200" in str(exc_info.value).lower()
