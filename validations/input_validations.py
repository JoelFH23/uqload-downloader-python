import re

def is_string_empty(string: str) -> bool:
    if not isinstance(string, str) or not len(string):
        return True
    return False

def is_uqload_url(url: str) -> bool:
    uqload_regex = r"https?://(?:www\.)?uqload\.io?/(?:embed-)?[a-zA-Z0-9]+\.(html)$"
    return bool(re.search(uqload_regex, url))

def remove_special_characters(string: str) -> str:
    pattern = r'[^a-zA-Z0-9]'
    # replace the matched pattern with ' '
    return re.sub(pattern, ' ', string)
