import re, urllib.request
from uuid import uuid4
from uqload_dl.parallel_url_fetcher import ParallelURLFetcher
from uqload_dl.utils import (
    is_uqload_url,
    remove_special_characters,
    is_a_callback,
    is_a_valid_directory,
    validate_output_file,
)
from uqload_dl.file_downloader import FileDownloader
from uqload_dl.exceptions import VideoNotFound
from typing import Dict, Callable, Union


class UQLoad:
    """
    Handles video information retrieval and downloading from UQload.io.
    """

    def __init__(
        self,
        url: str,
        output_file: str = None,
        output_dir: str = None,
        on_progress_callback: Callable = None,
    ) -> None:
        """
        Initializes the UQLoad instance.

        Args:
            url (str): The UQload video URL.
            output_file (Optional[str], optional): Custom name for the output file.
            output_dir (Optional[str], optional): Directory where the video will be saved.
            on_progress_callback (Optional[Callable], optional): A function to report download progress.

        Raises:
            ValueError: If the URL is invalid.
        """
        self.__video_info: Dict[str, Union[str, None]] = {}
        self.url = self.__validate_url(url)
        self.output_dir = is_a_valid_directory(output_dir)
        self.output_file = self.__validate_output_file(output_file)
        self.on_progress_callback = is_a_callback(on_progress_callback)

    def __validate_output_file(self, output_file: str = None) -> Union[str, None]:
        """
        Validates and sanitizes the output file name.

        Args:
            output_file (Optional[str]): The proposed file name.

        Returns:
            Optional[str]: A sanitized file name, or None if not provided.

        Raises:
            ValueError: If the file name is invalid.
        """
        if output_file is None:
            return None
        return validate_output_file(output_file)

    def __validate_url(self, url: str) -> str:
        """
        Validates and formats a UQload URL.

        Args:
            url (str): The input URL.

        Returns:
            str: A validated and formatted embed URL.

        Raises:
            ValueError: If the URL is invalid or does not match UQload patterns.
        """
        if url is None or not isinstance(url, str) or len(url) < 12:
            raise ValueError("Invalid Uqload URL. Please try again.")

        parts = url.rsplit("/", 1)
        base_url = parts[0] if len(parts) == 2 else "https://uqload.cx"
        video_id = parts[-1]

        video_id = f"{video_id}.html" if ".html" not in video_id else video_id
        video_id = f"embed-{video_id}" if "embed-" not in video_id else video_id

        full_url = f"{base_url}/{video_id}"

        if not is_uqload_url(full_url):
            raise ValueError("Invalid Uqload URL. Please try again.")

        return full_url

    def __get_video(self) -> None:
        """
        Retrieves video data from UQload and prepares the downloader.

        Raises:
            ValueError: If network content is missing.
            VideoNotFound: If the video has been deleted or not found.
        """
        print(f"Looking for video...")

        urls = [self.url, self.url.replace("embed-", "")]
        responses = ParallelURLFetcher(urls).fetch_all()

        if responses[0] is None and responses[1] is None:
            raise ValueError("No content")

        if "File was deleted" in responses[0]:
            raise VideoNotFound("The video has been deleted or does not exist")

        response_text_0, response_text_1 = responses

        matches = re.findall(r"https?://.+/v\.mp4", response_text_0)
        if not matches:
            raise VideoNotFound("The video has been deleted or does not exist")

        video_url = matches[0]
        image_url = re.findall(r"https?://.*?\.jpg", response_text_0)[0]
        title_match = re.findall(r'title:\s*"([^"]+)"', response_text_0)
        title = title_match[0] if title_match else "video"

        # NOTE: sometimes the duration and resolution may not be available.

        resolution = duration = None

        class_names = re.findall(r'class\s*=\s*[\'"]([^\'" ]+)[\'"]', response_text_1)
        if not "err" in class_names:
            h1_match = re.findall(r"<h1[^>]*>(.*?)</h1>", response_text_1, re.DOTALL)
            if h1_match:
                title = remove_special_characters(" ".join(h1_match[0].split()))

            textarea_content = re.findall(
                r"<textarea[^>]*>(.*?)</textarea>", response_text_1, re.DOTALL
            )
            pattern = r"\[(\d+x\d+)\, ((\d+:)*\d+)\]"
            for text in textarea_content:
                match = re.search(pattern, text)
                if match:
                    resolution, duration = match.group(1), match.group(2)
                    break

        final_title = remove_special_characters(title)
        if not self.output_file:
            self.output_file = final_title or uuid4().hex

        self.__downloader = FileDownloader(
            url=video_url,
            filename=self.output_file,
            output_dir=self.output_dir,
            on_progress_callback=self.on_progress_callback,
        )

        self.__video_info = {
            "url": video_url,
            "title": self.output_file,
            "image_url": image_url,
            "resolution": resolution,
            "duration": duration,
            "size": self.__downloader.total_size,
            "type": self.__downloader.type,
        }

    def get_video_info(self) -> Dict[str, str]:
        """
        Returns detailed information about the video.

        Returns:
            Dict[str, Union[str, None]]: A dictionary containing video metadata.
        """
        if not self.__video_info:
            self.__get_video()
        return self.__video_info

    def download(self) -> None:
        """
        Downloads the video to the specified output directory.
        """
        if not self.__video_info:
            self.__get_video()
        self.__downloader.download()
