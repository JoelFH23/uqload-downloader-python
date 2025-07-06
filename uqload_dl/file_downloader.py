import re, os, urllib
from uqload_dl.utils import is_a_callback, is_a_valid_directory, validate_output_file
from urllib.parse import urlparse
from typing import Callable
from uuid import uuid4

# Test: https://sampletestfile.com/wp-content/uploads/2023/07/15MB-MP4.mp4


class FileDownloader:
    """
    Downloads a file from a given URL and saves it locally.

    Args:
        url (str): The URL of the file to download.
        filename (str, optional): Custom name for the output file.
        output_dir (str, optional): Directory where file will be saved.
        on_progress_callback (Callable, optional): Callback for download progress.

    Raises:
        ValueError: On invalid input arguments or download issues.
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
        self.output_dir = is_a_valid_directory(output_dir)
        self.on_progress_callback = is_a_callback(on_progress_callback)
        self.__get_metadata()
        self.destination = None
        self.bytes_downloaded = 0

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
            ValueError: If the URL is invalid.
        """
        if url is None or not isinstance(url, str) or not len(url):
            raise ValueError("URL must be a non-empty string.")

        pattern = r"^https?://.+\.\w+$"
        if not re.match(pattern, url):
            raise ValueError("Invalid URL: URL does not contain a file extension")

        parsed = urlparse(url)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
                "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
            ),
            "Referer": f"{parsed.scheme}://{parsed.netloc}",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
        }

        self.name, self.__extension = os.path.splitext(os.path.basename(url))

        return url

    def __get_metadata(self) -> None:
        """
        Retrieves file metadata (size and type).

        Raises:
            ValueError: On HTTP issues or missing metadata.
        """
        try:
            request = urllib.request.Request(
                self.url, headers=self.headers, method="HEAD"
            )
            with urllib.request.urlopen(request) as response:
                if response.getcode() != 200:
                    raise ValueError("Received non-200 HTTP response")

                self.total_size = int(response.info().get("Content-Length", 0))

                if not self.total_size:
                    raise ValueError("Missing Content-Length in response")

                self.type = response.info().get("Content-Type", "")
        except urllib.error.HTTPError as e:
            raise ValueError(f"FileDownloader HTTPErrpr {self.url}: {e}") from e
        except urllib.error.URLError as e:
            raise ValueError(f"FileDownloader URLErrpr {self.url}: {e}") from e
        except Exception as e:
            raise ValueError(f"FileDownloader Unexpected error {self.url}: {e}") from e

    @property
    def filename(self) -> str:
        """Returns the output filename."""
        return self.__filename

    def delete_file(self) -> None:
        """Deletes the downloaded file if it exists."""
        if os.path.exists(self.destination):
            print(f"deleted : {self.destination}")
            os.remove(self.destination)

    def download(self) -> None:
        """
        Downloads the file from the URL.

        Raises:
            ValueError: If the file cannot be downloaded.
            KeyboardInterrupt: If interrupted by user.
            Exception: For other errors.
        """
        try:
            request = urllib.request.Request(self.url, headers=self.headers)
            with urllib.request.urlopen(request) as response:
                if response.getcode() != 200:
                    raise ValueError("file cannot be downloaded")

                self.destination = os.path.join(
                    self.output_dir, f"{self.__filename}{self.__extension}"
                )

                # Avoid overwrite
                if os.path.isfile(self.destination):
                    self.destination = os.path.join(
                        self.output_dir,
                        f"{self.__filename}_{uuid4().hex}{self.__extension}",
                    )

                with open(self.destination, "wb") as file:
                    while chunk := response.read(8192):
                        file.write(chunk)
                        self.bytes_downloaded += len(chunk)
                        if self.on_progress_callback:
                            self.on_progress_callback(
                                self.bytes_downloaded, self.total_size
                            )
                print(f"\nFile saved as: {self.destination}")

        except urllib.error.HTTPError as error:
            print(f"\nHTTP ERROR: {str(error)}")
        except KeyboardInterrupt:
            print("\nDownload cancelled by user.")
        except Exception as ex:
            print(f"\nUnexpected error: {ex}")
