import urllib.request
from threading import Thread
from typing import List, Optional, Tuple


class ParallelURLFetcher:
    """
    Fetches multiple URLs concurrently using threads.

    This class is designed to send parallel HTTP GET requests to a list of URLs,
    and collect their response content (decoded as UTF-8 text).
    """

    def __init__(self, urls: List[str]) -> None:
        """
        Initializes the fetcher with a list of URLs.

        Args:
            urls (List[str]): List of non-empty URL strings.

        Raises:
            ValueError: If the list is empty or contains invalid items.
        """
        self._urls = self._validate_urls(urls)
        self._indexed_responses: List[Tuple[int, Optional[str]]] = []

    def _validate_urls(self, urls: List[str]) -> List[str]:
        """
        Validates that the input is a non-empty list of non-empty strings.

        Args:
            urls (List[str]): List of URLs to validate.

        Returns:
            List[str]: The validated list of URLs.

        Raises:
            ValueError: If the list is empty or contains invalid items.
        """
        if not urls or not all(isinstance(url, str) and url.strip() for url in urls):
            raise ValueError("The URL list must contain non-empty strings.")
        return urls

    def _fetch_single_url(self, url: str, index: int) -> None:
        """
        Fetches a single URL and stores the response content.

        Args:
            url (str): The URL to fetch.
            index (int): The index in the original URL list (for ordering).
        """
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                    "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
                ),
                "Referer": "https://www.google.com",
                "Accept-Language": "en-US,en;q=0.9",
            }
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.getcode() == 200:
                    content = response.read().decode("utf-8")
                    self._indexed_responses.append((index, content))
                else:
                    self._indexed_responses.append((index, None))
        except Exception as ex:
            self._indexed_responses.append((index, None))
            print("ERROR: ParallelURLFetcher ", ex)

    def _run_fetch_threads(self) -> None:
        """
        Starts and joins threads for fetching all URLs in parallel.
        """
        threads: List[Thread] = []
        for idx, url in enumerate(self._urls):
            thread = Thread(target=self._fetch_single_url, args=(url, idx))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def fetch_all(self) -> List[Optional[str]]:
        """
        Initiates the fetching process for all URLs and returns responses in order.

        Returns:
            List[Optional[str]]: A list of response contents (as text), ordered by original input.
                                 If a URL fails or does not return 200, its position will be None.
        """
        self._run_fetch_threads()
        return [resp for _, resp in sorted(self._indexed_responses)]
