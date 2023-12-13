import re, os, httpx
from uqload_dl.utils import is_a_callback, is_a_valid_directory, validate_output_file
from urllib.parse import urlparse
from typing import Callable
from uuid import uuid4

# Test: https://assets.mixkit.co/videos/preview/mixkit-white-cat-lying-among-the-grasses-seen-up-close-22732-large.mp4


class FileDownloader:
    """
    Class to download a file using the url.

    Args:
        url (str): The URL of the file to download.
        filename (str, Optional): The name of the file to be saved as.
        output_dir (str, Optional): The directory where the file will be saved.
        on_progress_callback (Callable, Optional): A callback function that will be called
        with the downloaded size and total size as arguments.

    Raises:
        ValueError: If URL validation fails for provided URL.
    """

    def __init__(
        self,
        url: str,
        filename: str = None,
        output_dir: str = None,
        on_progress_callback: Callable = None,
    ) -> None:
        self.url = self.__validate_url(url)
        self.__filename = self.__validate_output_file(filename)
        self.outpur_dir = is_a_valid_directory(output_dir)
        self.on_progress_callback = is_a_callback(on_progress_callback)
        self.__get_metadata()

    def __validate_output_file(self, filename: str = None) -> str:
        """
        Validates the output filename.

        If filename is None (default) the url will be used as filename.
        For example: https://example.com/my_file.txt the filename will be: my_file.txt

        Args:
            filename (str,None): the filename.

        Returns:
            filename (str): A sanitized output file name.

        Raises:
            ValueError: If the provided filename is not a valid string, is empty, or contains only special characters.
        """
        if filename is None:
            return self.name
        return validate_output_file(filename)

    def __validate_url(self, url: str) -> str:
        """
        Validates the URL and sets headers for request.

        Args:
            url (str): A string representing the URL.

        Returns:
            The validated URL.

        Raises:
            ValueError: If the URL is None, empty, not a string, or lacks a file extension.
        """
        if url is None or not isinstance(url, str) or not len(url):
            raise ValueError("URL must be a non-empty string.")

        pattern = r"^https?://.+\.\w+$"
        if not re.match(pattern, url):
            raise ValueError("Invalid URL: URL does not contain a file extension")

        parsed_uri = urlparse(url)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Referer": f"{parsed_uri.scheme}://{parsed_uri.netloc}",
        }

        self.name, self.__extension = os.path.splitext(os.path.basename(url))

        return url

    def __get_metadata(self) -> None:
        """
        Fetches metadata for the download.

        Raises:
            ValueError: If the content-length does not exist in the header or the status code is not 200.
        """
        with httpx.Client() as client:
            response = client.head(
                self.url, headers=self.headers, follow_redirects=True, timeout=40
            )
            if response.status_code != 200:
                raise ValueError("Non-200 status code received")

            content_length = int(response.headers.get("content-length", 0))
            content_type = str(response.headers.get("content-type", ""))

            if not content_length:
                raise ValueError("Content length is missing")

            self.total_size = content_length
            self.type = content_type

    @property
    def get_filename(self) -> str:
        """Gets the filename."""
        return self.__filename

    def delete_file(self) -> None:
        """Deletes the file if it exists."""
        if os.path.isfile(self.destination):
            print(f"deleted : {self.destination}")
            os.remove(self.destination)

    def download(self) -> None:
        """
        Downloads the file.

        Raises:
            KeyboardInterrupt: If the user presses Ctrl+C.
            ValueError: The status code is not 200.
            HTTPStatusError: Any HTTP error.
        """
        try:
            with httpx.stream(
                method="GET",
                url=self.url,
                headers=self.headers,
                follow_redirects=True,
                timeout=40,
            ) as response:
                response.raise_for_status()

                if response.status_code != 200:
                    raise ValueError("file cannot be downloaded")

                self.destination = os.path.join(
                    self.outpur_dir, f"{self.__filename}{self.__extension}"
                )
                # check if the file already exist
                if os.path.isfile(self.destination):
                    self.destination = os.path.join(
                        self.outpur_dir,
                        f"{self.__filename}_{uuid4().hex}{self.__extension}",
                    )

                self.bytes_downloaded = 0
                with open(self.destination, "wb") as file:
                    for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                        file.write(chunk)
                        self.bytes_downloaded += len(chunk)
                        if self.on_progress_callback:
                            self.on_progress_callback(
                                self.bytes_downloaded, self.total_size
                            )
                print(f"\nVideo saved as: {self.destination}")

        except httpx.HTTPStatusError as error:
            print(f"\nHTTP ERROR: {str(error)}")
        except KeyboardInterrupt:
            print(f"\nOperation canceled")
        except Exception as ex:
            print(f"\nAn error occurred: {str(ex)}")
