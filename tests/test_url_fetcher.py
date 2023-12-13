import pytest
from pytest_httpx import HTTPXMock
from uqload_dl.url_fetcher import URLFetcher


@pytest.mark.parametrize(
    "value",
    [
        ([]),
        (""),
        ("test"),
        ([""]),
        ([12, 2, 2]),
        ([{"key": "value"}]),
        ([123, 23, 4, 3]),
        ([[], "b"]),
        (["a", True]),
        (["a", "b", ""]),
        (["a", "b", []]),
        ([["a", "b", ""]]),
    ],
)
def test_constructor_incorrect_params(value) -> None:
    with pytest.raises(ValueError):
        URLFetcher(url_list=value)


@pytest.mark.parametrize(
    "value",
    [(["a", "b", "c"]), (["test string"]), (["https", "https", "https://"])],
)
def test_constructor_correct_params(value) -> None:
    URLFetcher(url_list=value)


def test_make_request_successful(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        status_code=200,
        text="OK",
    )

    fetcher_instance = URLFetcher(url_list=["https://success.com"])
    responses = fetcher_instance.start()

    assert len(responses) == 1
    assert responses[0].status_code == 200
    assert responses[0].text == "OK"


def test_make_request_failed(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        url="https://not_found.com", status_code=404, text="Not Found"
    )
    httpx_mock.add_response(
        url="https://internal_server_error.com",
        status_code=500,
        text="Internal Server Error",
    )

    fetcher_instance = URLFetcher(
        url_list=[
            "https://not_found.com",
            "https://internal_server_error.com",
        ]
    )
    responses = fetcher_instance.start()

    assert responses == [None, None]
