import os, mimetypes, pytest
from pytest_httpx import HTTPXMock
from uqload_dl.file_downloader import FileDownloader

# image: https://www.awsfzoo.com/media/1J3A7944-scaled.jpg


@pytest.mark.parametrize(
    "url",
    [
        (""),
        ("https://test.com.mx/no_extension"),
        (None),
        (True),
        ([]),
        ({}),
    ],
)
def test_incorrect_url(url) -> None:
    with pytest.raises(ValueError):
        FileDownloader(url)


def test_no_filename(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        headers={"Content-Length": "24"}, status_code=200, method="HEAD"
    )

    assert (
        FileDownloader(url="https://test.com.mx/the_best_file_name.jpg").get_filename
        == "the_best_file_name"
    )

    assert (
        FileDownloader(
            url="https://test.com.mx/the_best_file_name.jpg",
            filename="SpongeBob SquarePants",
        ).get_filename
        == "SpongeBob SquarePants"
    )


def test_incorrect_filename() -> None:
    with pytest.raises(ValueError):
        FileDownloader(url="https://test.com.mx/video.mkv", filename="{}{},,::")


def test_remove_special_characters_in_filename(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        headers={"Content-Length": "24"}, status_code=200, method="HEAD"
    )
    assert (
        FileDownloader(
            url="https://test.com.mx/spongebob.jpg",
            filename="Filename ¡@@? with,::.special##characters!",
        ).get_filename
        == "Filename with special characters"
    )


def test_incorrect_output_dir() -> None:
    with pytest.raises(ValueError):
        FileDownloader(
            url="https://test.com.mx/video.mkv",
            filename="SpongeBob SquarePants",
            output_dir=__file__,
        )


def test_make_request_with_non_200_status_code(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(status_code=404, text="Not found.")
    with pytest.raises(ValueError):
        FileDownloader(url="https://test.com.mx/not_found.jpg").download()


def test_download_image(httpx_mock: HTTPXMock) -> None:
    file_path = "media/python.jpg"
    file_size = os.path.getsize(file_path)
    content_type = mimetypes.guess_type(file_path)[0]

    headers = {"Content-Type": content_type, "Content-Length": str(file_size)}

    with open(file_path, "rb") as image_file:
        image_content = image_file.read()
        httpx_mock.add_response(headers=headers, content=image_content, status_code=200)

    downloader = FileDownloader(url="https://test.com.mx/test_mock_image.jpg")
    downloader.download()
    assert downloader.total_size == file_size
    # Clean up the test file
    downloader.delete_file()


def test_download_video(httpx_mock: HTTPXMock) -> None:
    file_path = "media/patrick_rides_a_seahorse.mp4"
    file_size = os.path.getsize(file_path)
    content_type = mimetypes.guess_type(file_path)[0]

    headers = {"Content-Type": content_type, "Content-Length": str(file_size)}

    with open(file_path, "rb") as video_file:
        video_content = video_file.read()
        httpx_mock.add_response(headers=headers, content=video_content, status_code=200)

    downloader = FileDownloader(url="https://test.com.mx/test_mock_video.mp4")
    downloader.download()
    assert os.path.isfile(f"{downloader.get_filename}.mp4") == True
    assert downloader.type == content_type
    assert downloader.total_size == file_size
    # Clean up the test file
    downloader.delete_file()
