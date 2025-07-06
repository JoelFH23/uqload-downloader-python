import pytest
from unittest.mock import patch
from uqload_dl.uqload import UQLoad
from uqload_dl.exceptions import VideoNotFound
from typing import Dict


@pytest.fixture
def sample_data() -> Dict[str, str]:
    return {
        "valid_url": "https://uqload.cx/vule3vel9n5q.html",
        "formatted_url": "https://uqload.cx/embed-vule3vel9n5q.html",
        "video_response": '<video src="https://m180.uqload.cx/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6j7tq2bdq4q/v.mp4"></video><img src="https://m180.uqload.cx/i/05/02288/vule3vel9n5q_xt.jpg"><script>title: "My Title"</script>',
        "embed_response": "<h1>My Embed Title</h1><textarea>[1920x1080, 01:23]</textarea>",
    }


def test_invalid_url_raises_value_error() -> None:
    with pytest.raises(ValueError):
        UQLoad("invalid_url")


@pytest.mark.parametrize(
    "output_file",
    [(True), (""), (123)],
)
def test_invalid_output_file_raises(output_file) -> None:
    with pytest.raises(ValueError):
        UQLoad("https://uqload.cx/vule3vel9n5q.html", output_file=output_file)


@patch("uqload_dl.uqload.ParallelURLFetcher")
@patch("uqload_dl.uqload.FileDownloader")
def test_get_video_info_success(
    mock_downloader, mock_fetcher, sample_data: Dict[str, str]
) -> None:
    mock_fetcher.return_value.fetch_all.return_value = [
        sample_data["video_response"],
        sample_data["embed_response"],
    ]

    mock_downloader.return_value.total_size = 12345
    mock_downloader.return_value.type = "video/mp4"

    uq = UQLoad(sample_data["valid_url"])
    info = uq.get_video_info()

    assert info["url"].endswith("v.mp4")
    assert info["image_url"].endswith(".jpg")
    assert info["title"] == "My Embed Title"
    assert info["resolution"] == "1920x1080"
    assert info["duration"] == "01:23"
    assert info["size"] == 12345
    assert info["type"] == "video/mp4"


@patch("uqload_dl.uqload.ParallelURLFetcher")
@patch("uqload_dl.uqload.FileDownloader")
def test_download_triggers_fetch_and_download(
    mock_downloader, mock_fetcher, sample_data: Dict[str, str]
) -> None:
    mock_fetcher.return_value.fetch_all.return_value = [
        sample_data["video_response"],
        sample_data["embed_response"],
    ]
    mock_downloader.return_value.total_size = 100
    mock_downloader.return_value.type = "video/mp4"

    uq = UQLoad(sample_data["valid_url"])
    uq.download()

    assert mock_downloader.return_value.download.called


@patch("uqload_dl.uqload.ParallelURLFetcher")
def test_video_not_found_deleted_file(
    mock_fetcher, sample_data: Dict[str, str]
) -> None:
    mock_fetcher.return_value.fetch_all.return_value = [
        "File was deleted",
        sample_data["embed_response"],
    ]
    uq = UQLoad(sample_data["valid_url"])
    with pytest.raises(VideoNotFound):
        uq.get_video_info()


@patch("uqload_dl.uqload.ParallelURLFetcher")
def test_video_not_found_missing_mp4(mock_fetcher, sample_data: Dict[str, str]) -> None:
    mock_fetcher.return_value.fetch_all.return_value = [
        "<html>no video here</html>",
        sample_data["embed_response"],
    ]
    uq = UQLoad(sample_data["valid_url"])
    with pytest.raises(VideoNotFound):
        uq.get_video_info()
