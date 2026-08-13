import pytest
from uqload_dl.utils import remove_special_characters, format_size


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
    "input_bytes, expected",
    [
        (0, 0),
        (512, "512.00 B"),
        (1023, "1023.00 B"),
        (1024, "1.00 KB"),
        (1536, "1.50 KB"),
        (1048576, "1.00 MB"),
        (1073741824, "1.00 GB"),
        (1099511627776, "1.00 TB"),
        (1125899906842624, "1024.00 TB"),
        (1.5 * 1024**2, "1.50 MB"),
    ],
)
def test_sizeof_fmt(input_bytes, expected):
    assert format_size(input_bytes) == expected
