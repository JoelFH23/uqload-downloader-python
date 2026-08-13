import re
from typing import Literal


def format_size(size_in_bytes: int) -> str | Literal[0]:
    if size_in_bytes == 0:
        return 0
    for unit in ["B", "KB", "MB", "GB"]:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"


def remove_special_characters(input_string: str) -> str:
    """
    Removes special characters from a string, leaving only alphanumeric characters,
    spaces, hyphens, underscores, and certain accented characters.

    Note: if only invalid characters are entered, an empty string will be returned.

    Args:
        input_string (str): The input string to clean.

    Returns:
        str: The cleaned string.
    """
    if (
        input_string is None
        or not isinstance(input_string, str)
        or not len(input_string)
    ):
        raise ValueError("input_string must be a non-empty string")
    pattern = r"[^a-zA-Z0-9\s\-\_áéíóúñÁÉÍÓÚÑüÜ]"
    cleaned_string = re.sub(pattern, " ", input_string)

    return " ".join((cleaned_string.split()))
