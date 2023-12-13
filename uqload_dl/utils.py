import re, os
from typing import Callable, Union


def validate_output_file(output_file: str) -> str:
    """
    Validates and sanitizes the output file name.

    Args:
        output_file (str): A string representing the output file name.

    Returns:
        str: A sanitized output file name.

    Raises:
        ValueError: If the provided output_file is None, not a valid string, empty, or contains only special characters.
    """
    if output_file is None or not isinstance(output_file, str) or not len(output_file):
        raise ValueError("Invalid output_file")
    # Sanitize output_file by removing special characters
    result = remove_special_characters(output_file)
    if not len(result):
        # Raise ValueError if the sanitized result is empty
        raise ValueError("Invalid output_file")
    return result


def is_a_valid_directory(output_dir: str = None) -> str:
    """
    Validates and returns a valid output directory path.

    Return current working directory if output_dir is None (default).

    Args:
        output_dir (str): A string representing the output directory path.

    Returns:
        str: A validated output directory path.

    Raises:
        ValueError: If the provided output_dir is not a valid string or doesn't exist as a directory.
    """
    if output_dir is None:
        return os.getcwd()
    elif not isinstance(output_dir, str) or not os.path.isdir(output_dir):
        raise ValueError("Invalid folder path")
    return output_dir


def is_a_callback(callback: Callable = None) -> Union[Callable, None]:
    """
    Executes the provided callback function if it's callable.

    Args:
        callback: A callable function.

    Returns:
        callable: The provided callback function if it's callable.
        None: if the callback is None (default).

    Raises:
        ValueError: If the callback is not callable.
    """
    if callback is None:
        return None  # Return None if callback is None
    elif not callable(callback):
        # Raise ValueError for non-callable callback
        raise ValueError("Callback must be a callable")
    return callback


def is_uqload_url(url: str) -> bool:
    """
    Checks if the provided URL is a valid Uqload URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is a valid Uqload URL, False otherwise.
    """
    if url is None:
        return False
    uqload_regex = (
        r"^https?://(www\.)?uqload\.(io|com|co)/(embed\-)?[a-zA-Z0-9]{12}\.(html)$"
    )
    if not isinstance(url, str) or not re.match(uqload_regex, url):
        return False
    return True


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
