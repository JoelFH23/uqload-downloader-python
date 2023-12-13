import pytest, os, mimetypes
from pytest_httpx import HTTPXMock
from uqload_dl.uqload import UQLoad
from uqload_dl.exceptions import VideoNotFound


@pytest.mark.parametrize(
    "url,output_file,output_dir",
    [
        (None, None, None),
        ("abcdefghijkl", "", None),
        ("abcdefghijkl", ".....", None),
        ("abcdefghijkl", "{}{}[]", None),
        ([], None, None),
        (["abcdefghijkl"], "my_video.mp4", None),
        ("abcdefghijkl", "my_video.mp4", "this folder does not exist"),
        ("abcdefghijkl", "my_video.mp4", os.path.abspath(__file__)),
        ([1, 2, 3], [None], None),
        ([[]], None, None),
        ("", None, None),
        ("embedabcdefghijkl", None, {}),
        ("abcdefghijk", None, [None] * 4),
        ("embed-abcdefghijkl.xml", None, os.path.abspath(__file__)),
        ("-abcdefghijkl", None, None),
        ("embed-abcdefghijkl.pdf", None, None),
        ("uqload.io/embed-abcdefghijkl.html", None, None),
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", None, None),
        (
            "https://media.tenor.com/vaUE_cMRWw0AAAAC/patrick-riding-seahorse.gif",
            None,
            None,
        ),
    ],
)
def test_constructor_incorrect_params(url, output_file, output_dir) -> None:
    with pytest.raises(ValueError):
        UQLoad(url, output_file, output_dir)


@pytest.mark.parametrize(
    "url,output_file,output_dir",
    [
        ("abcdefghijkl", None, None),
        ("abcdefghijkl.html", "my video", os.getcwd()),
        ("embed-abcdefghijkl.html", None, None),
        ("embed-abcdefghijkl", None, None),
        ("https://uqload.io/embed-abcdefghijkl.html", None, None),
    ],
)
def test_constructor_correct_params(url, output_file, output_dir) -> None:
    uqload_instance = UQLoad(url, output_file, output_dir)
    assert uqload_instance.output_file == output_file


def test_id() -> None:
    assert UQLoad("abcdefghijkl").url == "https://uqload.io/embed-abcdefghijkl.html"
    assert (
        UQLoad("abcdefghijkl.html").url == "https://uqload.io/embed-abcdefghijkl.html"
    )
    assert (
        UQLoad("embed-abcdefghijkl").url == "https://uqload.io/embed-abcdefghijkl.html"
    )


def test_get_video_info(httpx_mock: HTTPXMock) -> None:
    video_url = "https://m180.uqload.io/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6jzqldsce4q/v.mp4"

    with open("html/embed.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/embed-xxxxxxxxxxxx.html",
        status_code=200,
        html=html_content,
    )

    with open("html/home.html", "r", encoding="utf-8") as file:
        home_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/xxxxxxxxxxxx.html",
        status_code=200,
        html=home_content,
    )

    httpx_mock.add_response(
        url=video_url,
        method="HEAD",
        headers={"Content-Length": "24", "Content-Type": "video/mp4"},
        status_code=200,
        content=b"This is the video content",
    )

    uqload_instance = UQLoad(url="xxxxxxxxxxxx")
    video_info = uqload_instance.get_video_info()

    assert isinstance(video_info, dict)
    assert len(video_info) == 7

    assert video_info.get("size") == 24
    assert video_info.get("title") == "python testing time"
    assert video_info.get("url") == video_url
    assert video_info.get("type") == "video/mp4"
    assert (
        video_info.get("image_url")
        == "https://m180.uqload.io/i/05/02288/vule3vel9n5q_xt.jpg"
    )


def test_get_video_info_failed(httpx_mock: HTTPXMock) -> None:
    with open("html/home_video_not_found.html", "r", encoding="utf-8") as file:
        home_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/xxxxxxxxxxxx.html",
        status_code=200,
        html=home_content,
    )
    with open("html/embed_video_not_found.html", "r", encoding="utf-8") as file:
        embed_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/embed-xxxxxxxxxxxx.html",
        status_code=200,
        html=embed_content,
    )
    with pytest.raises(VideoNotFound):
        UQLoad(url="xxxxxxxxxxxx").get_video_info()


def test_get_video_info_embed_only(httpx_mock: HTTPXMock) -> None:
    video_url = "https://m180.uqload.io/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6jzqldsce4q/v.mp4"

    with open("html/home_video_not_found.html", "r", encoding="utf-8") as file:
        home_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/xxxxxxxxxxxx.html",
        status_code=200,
        html=home_content,
    )

    with open("html/embed.html", "r", encoding="utf-8") as file:
        embed_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/embed-xxxxxxxxxxxx.html",
        status_code=200,
        html=embed_content,
    )

    httpx_mock.add_response(
        url=video_url,
        method="HEAD",
        status_code=200,
        content=b"This is the video content",
        headers={"Content-Length": "24", "Content-Type": "video/mp4"},
    )
    uqload_instance = UQLoad(url="xxxxxxxxxxxx")
    video_info = uqload_instance.get_video_info()
    assert len(video_info) == 7
    assert video_info.get("url") == video_url
    assert video_info.get("type") == "video/mp4"
    assert video_info.get("size") == 24


def test_download_video(httpx_mock: HTTPXMock) -> None:
    video_url = "https://m180.uqload.io/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6jzqldsce4q/v.mp4"

    with open("html/embed.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/embed-xxxxxxxxxxxx.html",
        status_code=200,
        html=html_content,
    )
    with open("html/home.html", "r", encoding="utf-8") as file:
        home_content = file.read()
    httpx_mock.add_response(
        url="https://uqload.io/xxxxxxxxxxxx.html",
        status_code=200,
        html=home_content,
    )

    file_path = "media/patrick_rides_a_seahorse.mp4"
    file_size = os.path.getsize(file_path)
    content_type = mimetypes.guess_type(file_path)[0]

    headers = {"Content-Type": content_type, "Content-Length": str(file_size)}

    with open(file_path, "rb") as video_file:
        video_content = video_file.read()
        httpx_mock.add_response(
            url=video_url,
            method="HEAD",
            status_code=200,
            content=video_content,
            headers=headers,
        )
    with open(file_path, "rb") as video_file:
        video_content = video_file.read()
        httpx_mock.add_response(
            url=video_url,
            method="GET",
            status_code=200,
            content=video_content,
            headers=headers,
        )

    uqload_instance = UQLoad(url="xxxxxxxxxxxx", output_file="my video")
    video_info = uqload_instance.get_video_info()
    assert video_info.get("type") == content_type
    assert video_info.get("size") == file_size
    assert uqload_instance.output_file == "my video"

    uqload_instance.download()

    test_file_path = os.path.join(os.getcwd(), f"{uqload_instance.output_file}.mp4")
    assert os.path.isfile(test_file_path) == True

    # Clean up the test file
    if os.path.isfile(test_file_path):
        os.remove(test_file_path)
