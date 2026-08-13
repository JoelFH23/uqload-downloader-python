import pytest

from uqload_dl import UQload
from uqload_dl.exceptions import UQloadError


def test_validate_url() -> None:
    url = "https://uqload.is/abcd1234"

    video_id = UQload._validate_url(url)

    assert video_id == "abcd1234"


def test_validate_url_with_embed() -> None:
    url = "https://uqload.example/embed-abc123"

    video_id = UQload._validate_url(url)

    assert video_id == "abc123"


def test_validate_url_invalid() -> None:
    url = "https://example.com/abc123"

    with pytest.raises(ValueError, match="Invalid UQload URL"):
        UQload._validate_url(url)


def test_extract_qualities() -> None:
    html = """
    <table>
        <tr>
            <td><a href="https://example.com/video.mp4">Download</a></td>
            <td>720, 100 MB</td>
        </tr>
        <tr>
            <td><a href="https://example.com/video2.mp4">Download</a></td>
            <td>480, 50 MB</td>
        </tr>
    </table>
    """

    client = UQload.__new__(UQload)

    qualities = client._extract_qualities(html)

    assert len(qualities) == 2
    assert qualities[0].resolution == "720"
    assert qualities[0].size == "100 MB"
    assert qualities[0].url == "https://example.com/video.mp4"


def test_extract_qualities_not_found() -> None:
    html = "<html><body>No qualities</body></html>"

    client = UQload.__new__(UQload)

    with pytest.raises(UQloadError, match="Video quality could not be found"):
        client._extract_qualities(html)
