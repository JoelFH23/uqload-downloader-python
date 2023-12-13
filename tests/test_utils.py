import pytest, os
from typing import Literal
from uqload_dl.utils import (
    remove_special_characters,
    is_uqload_url,
    validate_output_file,
    is_a_valid_directory,
    is_a_callback,
)


@pytest.mark.parametrize(
    "value",
    [
        (True),
        (None),
        (""),
        ("!!!!!"),
        ([1, 2, 3]),
        ({"key": "value"}),
    ],
)
def test_invalid_output_file(value) -> None:
    with pytest.raises(ValueError):
        validate_output_file(value)


def test_valid_output_file() -> None:
    assert validate_output_file("test!") == "test"
    assert validate_output_file("filename") == "filename"


@pytest.mark.parametrize("value", [([None] * 4), ({}), (""), (True)])
def test_invalid_directory(value) -> None:
    with pytest.raises(ValueError):
        is_a_valid_directory(value)


def test_valid_directory() -> None:
    assert is_a_valid_directory(None) == os.getcwd()


def test_callback_none() -> None:
    assert is_a_callback() is None


def test_callback_callable() -> None:
    def sample_callback() -> Literal["Sample Callback"]:
        return "Sample Callback"

    assert is_a_callback(sample_callback) == sample_callback


def test_callback_not_callable() -> None:
    with pytest.raises(ValueError):
        is_a_callback(123)


@pytest.mark.parametrize("input_string", [(""), ([]), (None), (True), [[12, 3, 4, 5]]])
def test_remove_special_characters_incorrect_params(input_string) -> None:
    with pytest.raises(ValueError):
        remove_special_characters(input_string)


def test_remove_special_characters() -> None:
    assert remove_special_characters("test") == "test"
    assert remove_special_characters("this$$is a test!") == "this is a test"
    assert remove_special_characters("my video.mp4") == "my video mp4"
    assert remove_special_characters("My_underscore_string") == "My_underscore_string"
    assert remove_special_characters("%%&%$??!!??,,ñÑ{{}}$¡¿¿??") == "ñÑ"
    assert remove_special_characters("¡Estoy aquí!") == "Estoy aquí"
    assert remove_special_characters("passwords.txt") == "passwords txt"
    assert remove_special_characters("    python     ") == "python"
    assert remove_special_characters("Node 20.10.0") == "Node 20 10 0"
    assert (
        remove_special_characters("[python,ruby,php,javascript]")
        == "python ruby php javascript"
    )
    assert (
        remove_special_characters("El corazón late rápido cuando está emocionado.")
        == "El corazón late rápido cuando está emocionado"
    )


@pytest.mark.parametrize(
    "url",
    [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        (None),
        (True),
        (""),
        ([]),
        ({}),
        (
            "https://e7.pngegg.com/pngimages/782/228/png-clipart-ruby-on-rails-rubygems-amazon-dynamodb-ruby-text-logo.png"
        ),
        ("https://www.twitch.tv/twitch"),
        ("https://test.com/index.html"),
        ("https://uqload.io/embed-xxxxxxxxxxxx"),
        ("https://uqload.io/embed-embed-embed-xxxxxxxxxxx"),
        ("https://uqload.io/xxxxxxxxxxx"),
        ("https://www.uqload.io/-xxxxxxxxxxxx.html"),
        ("https://www.uqload.io/e-xxxxxxxxxxxx.html"),
        ("https://www.uqload.io/.html"),
        ("https://www.uqload.io"),
        ("https://uqload.io/embed-.html"),
        ("https://open.spotify.com/track/2ctvdKmETyOzPb2GiJJT53?si=52ba32b25f9a4a45"),
        ("uqload.io/embed-xxxxxxxxxxxx.html"),
        ("xxxxxxxxxxxx"),
        ("xxxxxxxxxxxx.html"),
    ],
)
def test_uqload_incorrect_url(url) -> None:
    assert is_uqload_url(url) == False


@pytest.mark.parametrize(
    "url",
    [
        ("https://uqload.io/embed-xxxxxxxxxxxx.html"),
        ("https://www.uqload.io/embed-xxxxxxxxxxxx.html"),
        ("https://uqload.io/embed-xxxxxxxxxxxx.html"),
        ("https://uqload.io/embed-xxxxxxxxxxxx.html"),
        ("http://uqload.io/embed-xxxxxxxxxxxx.html"),
        ("https://uqload.co/embed-xxxxxxxxxxxx.html"),
        ("https://uqload.com/embed-xxxxxxxxxxxx.html"),
        ("https://uqload.com/xxxxxxxxxxxx.html"),
        ("https://www.uqload.io/xxxxxxxxxxxx.html"),
    ],
)
def test_uqload_correct_url(url) -> None:
    assert is_uqload_url(url) == True
