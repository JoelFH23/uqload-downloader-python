import httpx, asyncio
from typing import List, Union, Tuple


class URLFetcher:
    """
    Class to send multiple HTTP requests in parallel.

    Attributes:
        url_list (list): List of urls
    """

    def __init__(self, url_list: List[str]) -> None:
        self.url_list = self.__validate_url_list(url_list)

    def __validate_url_list(self, url_list: list) -> list:
        """Validates that the list contains only non-empty strings

        Note: It only validates that they are not empty strings
        but not if they are valid URLs.

        Raises:
            ValueError: If url_list is an invalid list.

        Returns:
            list: The list of strings.
        """
        if url_list is None or not isinstance(url_list, list) or not len(url_list):
            raise ValueError("The url_list must be a non empty list")
        elif not all(isinstance(url, str) and len(url) != 0 for url in url_list):
            raise ValueError("The url_list must be a non empty list")
        return url_list

    async def __fetch_url(
        self, url: str, index: int
    ) -> Union[Tuple[int, httpx.Response], Tuple[int, None]]:
        """
        Make an asynchronous HTTP GET request using httpx.

        Args:
            url (str): The url to make the request.
            index (int): To know in which order the resquest were sent.

        Returns:
            tuple: index and response if status code is 200 otherwise index and None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=60, follow_redirects=True)
                if response.status_code == 200:
                    return index, response
                return index, None
        except Exception:
            return index, None

    async def __fetch_responses(self) -> List[Union[httpx.Response, None]]:
        """
        Create a list of asynchronous tasks to get the responses from URLs simultaneously.

        An index is added to maintain the original order of the URLs.

        Returns:
            list: The responses for each of the urls.
        """
        tasks = [
            self.__fetch_url(url, index) for index, url in enumerate(self.url_list)
        ]
        # Await and gather the responses using asyncio.gather
        responses = await asyncio.gather(*tasks)
        # Sort the responses based on their original order (index)
        return [response for _, response in sorted(responses)]

    def start(self) -> List[Union[httpx.Response, None]]:
        """
        Start requests.

        Returns:
            list: The responses for each of the urls.
        """
        return asyncio.run(self.__fetch_responses())
