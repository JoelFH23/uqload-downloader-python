import logging
import random
import time
import re

from uqload_dl.utils import remove_special_characters
from uqload_dl.models import VideoInfo, VideoQuality
from uqload_dl.constants import DEFAULT_HEADERS
from uqload_dl.exceptions import UQloadError

from urllib.parse import urlencode, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from typing import Dict, Callable, Tuple, List
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)


class UQload:
    def __init__(self, output_dir: str = "") -> None:
        """Initialize the UQload client.

        Args:
            output_dir: Directory where downloaded files will be stored.
                Defaults to the user's Downloads directory.
        """
        self.output_dir = UQload._validate_output_dir(output_dir)

    @staticmethod
    def _validate_output_dir(path: str) -> Path:
        """Validate and normalize the output directory.

        An empty path is replaced with the user's default Downloads
        directory.

        Args:
            path: Path to the directory where files will be downloaded.

        Returns:
            A validated directory path.

        Raises:
            ValueError: If the path is not a string or does not point
                to an existing directory.
        """
        if not isinstance(path, str):
            raise ValueError(f"Invalid or inaccessible path: {path}")

        if not path or not path.strip():
            path = Path.home() / "Downloads"
        else:
            path = Path(path)

        if not path.is_dir():
            raise ValueError(f"Invalid or inaccessible path: {path}")

        return path

    @staticmethod
    def _validate_url(url: str) -> str:
        """Validate a UQload URL and extract the video ID.

        Args:
            url: URL of the UQload video.

        Returns:
            The video ID extracted from the URL.

        Raises:
            ValueError: If the URL is not a valid UQload URL.
        """
        pattern = r"^https?://(?:[^/]+\.)?uqload\.[a-z]+/(?:embed-|d/)?([a-zA-Z0-9_-]+)(?:\.html)?(?:[?#].*)?$"
        match = re.match(pattern, url, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid UQload URL")
        return str(match.group(1))

    @staticmethod
    def _wait() -> None:
        """Wait for a random amount of time between requests."""
        delay = random.uniform(1, 1.5)
        logger.info(f"Waiting {delay} seconds...")
        time.sleep(delay)

    def _request(
        self, url: str, method: str = "GET", data: Dict[str, str] | None = None
    ) -> str:
        """Send an HTTP request to UQload.

        Args:
            url: URL to request.
            method: HTTP method to use.
                Defaults to ``"GET"``.
            data: Optional form data to send with the request.

        Returns:
            The response body decoded as a string.

        Raises:
            UQloadError: If the server returns an unexpected HTTP status
                code.
            HTTPError: If the request fails with an HTTP error.
            URLError: If the request fails due to a network error.
        """
        body = None
        if data:
            body = urlencode(data).encode()

        request = Request(
            url,
            method=method,
            data=body,
            headers=DEFAULT_HEADERS,
        )

        with urlopen(request, timeout=5) as response:
            if response.status != 200:
                raise UQloadError(f"Unexpected status code: {response.status}")

            return response.read().decode()

    @staticmethod
    def _validate_html_response(html: str) -> None:
        """Validate an HTML response for a missing video.

        Args:
            html: HTML response returned by UQload.

        Raises:
            UQloadError: If the response indicates that the requested
                video does not exist.
        """
        if "No such file" in html or "File Not Found" in html:
            raise UQloadError("Video not found.")

    def _extract_payload(self, html: str) -> Dict[str, str]:
        """Extract the download form payload from an HTML response.

        Args:
            html: HTML response containing the download form.

        Returns:
            A dictionary containing the form fields required to request
            the video download.

        Raises:
            UQloadError: If the expected download form cannot be found.
        """
        logger.info("Extracting payload...")
        form = re.search(
            r'<form[^>]*id="F1".*?>(.*?)</form>',
            html,
            re.DOTALL | re.IGNORECASE,
        )

        if form is None:
            raise UQloadError("Payload form not found.")

        inputs = re.findall(
            r'<input[^>]*name="(op|id|mode|hash)"[^>]*value="([^"]+)"',
            form.group(1),
            re.DOTALL | re.IGNORECASE,
        )
        return dict(inputs)

    def _extract_video_url_and_file_size(self, html: str) -> Tuple[str, int]:
        """Extract the direct video URL and file size from an HTML response.

        Args:
            html: HTML response containing the download information.

        Returns:
            A tuple containing the direct video URL and file size in bytes.

        Raises:
            UQloadError: If the direct video URL cannot be found.
        """
        logger.info("Extracting video URL and file size...")
        match = re.search(
            r'<a[^>]*href="([^"]+)"[^>]*class="[^"]*download-btn[^"]*"',
            html,
            re.DOTALL,
        )

        if match is None:
            raise UQloadError("MP4 URL not found.")

        file_size = 0
        for row in re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL):
            columns = re.findall(r"<td>(.*?)</td>", row, re.DOTALL)
            if not columns:
                continue
            if "bytes" in columns[0].split(" "):
                file_size = int(columns[0].split(" ")[0])
                break
        return (str(match.group(1)), file_size)

    def _extract_title_and_duration(self, html: str) -> Tuple[str, str | None]:
        """Extract the video title and duration from an HTML response.

        Args:
            html: HTML response containing the video metadata.

        Returns:
            A tuple containing the video title and duration. The duration
            is ``None`` if it cannot be found.

        Raises:
            UQloadError: If the HTML response indicates that the video
                does not exist.
        """
        UQload._validate_html_response(html)
        durantion = None
        for row in re.findall(r"<textarea[^>]*>(.*?)</textarea>", html, re.DOTALL):
            match = re.search(r"\[(\d+x\d+)\, ((\d+:)*\d+)\]", row)
            if match:
                durantion = str(match.group(2).strip())
                break

        title = f"video_{uuid4().hex}"
        match = re.search(
            r"<span[^>]*>\s*(.*?)\s*</span>", html, re.DOTALL | re.IGNORECASE
        )
        if match:
            title = str(match.group(1).strip())
        return (title, durantion)

    def _extract_qualities(self, html: str) -> List[VideoQuality]:
        """Extract the available video qualities from an HTML response.

        Args:
            html: HTML response containing the available video qualities.

        Returns:
            A list of available video qualities.

        Raises:
            UQloadError: If no video qualities can be found.
        """
        logger.info("Extracting the video qualities...")
        UQload._validate_html_response(html)

        qualities = []
        for row in re.findall(r"<tr>(.*?)</tr>", html, re.DOTALL):
            columns = re.findall(r"<td>(.*?)</td>", row, re.DOTALL)
            if len(columns) < 2:
                continue
            link = re.search(r'<a href="([^"]+)"', columns[0])
            if link is None:
                continue
            resolution, size = (item.strip() for item in columns[1].split(",", 1))
            qualities.append(
                VideoQuality(url=link.group(1), resolution=resolution, size=size)
            )
        if not qualities:
            raise UQloadError("Video quality could not be found.")
        return qualities

    def get_info(self, url: str) -> VideoInfo:
        """Retrieve metadata and download information for a video.

        The method retrieves the video title, duration, available
        qualities, direct MP4 URL, resolution, and file size.

        Args:
            url: UQload video URL.

        Returns:
            Information about the requested video.

        Raises:
            ValueError: If the provided URL is not a valid UQload URL.
            UQloadError: If the video cannot be found or the required
                information cannot be extracted.
            HTTPError: If an HTTP request fails.
            URLError: If a network error occurs.
        """
        video_id = UQload._validate_url(url)
        logger.info("Making a request to the website...")
        parsed = urlparse(url)
        main_url = f"https://{parsed.netloc}/{video_id}"
        sec_url = f"https://{parsed.netloc}/d/{video_id}"

        home_page = self._request(main_url)
        title, duration = self._extract_title_and_duration(home_page)
        UQload._wait()

        html = self._request(sec_url)
        qualities = self._extract_qualities(html)
        UQload._wait()

        download_page = self._request(qualities[0].url)
        payload = self._extract_payload(download_page)
        UQload._wait()

        html = self._request(url=qualities[0].url, method="POST", data=payload)
        mp4_url, file_size = self._extract_video_url_and_file_size(html)

        return VideoInfo(
            title=title,
            duration=duration,
            mp4_url=mp4_url,
            resolution=qualities[0].resolution,
            file_size=file_size,
        )

    def download(
        self,
        video_info: VideoInfo,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        """Download a video to the configured output directory.

        If a file with the same name already exists, a unique suffix is
        added to the filename.

        Args:
            video_info: Video information obtained from :meth:`get_info`.
            progress_callback: Optional callback invoked after each
                downloaded chunk. It receives the number of bytes
                downloaded and the total file size in bytes.

        Raises:
            ValueError: If ``video_info`` is not a :class:`VideoInfo`
                instance.
            HTTPError: If the server returns an HTTP error.
            URLError: If a network error occurs during the download.
            OSError: If the output file cannot be created or written.
        """

        if not isinstance(video_info, VideoInfo):
            raise ValueError("Invalid VideoInfo")

        parsed = urlparse(video_info.mp4_url)
        ext = parsed.path.rsplit(".", 1)[-1]
        filename = (
            self.output_dir / f"{remove_special_characters(video_info.title)}.{ext}"
        )
        if filename.is_file():
            filename = (
                self.output_dir
                / f"{remove_special_characters(video_info.title)}_{uuid4().hex[:12]}.{ext}"
            )
            logger.info(f"The file already exists! Changing the name to: {filename}")

        total_size = video_info.file_size
        req = Request(video_info.mp4_url, headers=DEFAULT_HEADERS)
        try:
            with urlopen(req) as response, open(filename, "wb") as out_file:
                chunk_size = 8192
                downloaded = 0

                logger.info("Downloading file...")
                while chunk := response.read(chunk_size):
                    out_file.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback:
                        progress_callback(downloaded, total_size)
        except HTTPError as e:
            logger.exception(f"HTTP Error downloading file: {e.code} - {e.reason}")
            raise
        except URLError as e:
            logger.exception(f"Network Error downloading file: {e.reason}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected system failure during file download: {e}")
            raise
