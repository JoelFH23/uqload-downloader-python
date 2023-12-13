import re, time
from uuid import uuid4
from uqload_dl.url_fetcher import URLFetcher
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
    Class to get information and download a video from UQload.

    Args:
        url (str): The UQload video url.
        output_file (str, optional): The name of the video.
        output_dir (str, optional): The directory where the file will be saved.
        on_progress_callback (callable, optional): A callback function that will be called
        with the downloaded size and total size as arguments.

    Raises:
        ValueError: If the URL is not valid.
    """

    def __init__(
        self,
        url: str,
        output_file: str = None,
        output_dir: str = None,
        on_progress_callback: Callable = None,
    ) -> None:
        self.__video_info = {}
        self.url = self.__validate_url(url)
        self.output_dir = is_a_valid_directory(output_dir)
        self.output_file = self.__validate_output_file(output_file)
        self.on_progress_callback = is_a_callback(on_progress_callback)

    def __validate_output_file(self, output_file: str = None) -> Union[str, None]:
        """
        Validates the output filename.

        Args:
            output_file (str, None): the filename.

        Returns:
            str: A sanitized output file.
            None: if output_file is None.

        Raises:
            ValueError: If the provided output_file is not a valid string, is empty, or contains only special characters.
        """
        if output_file is None:
            return None
        return validate_output_file(output_file)

    def __validate_url(self, url: str) -> str:
        """
        Validates and processes a Uqload URL.

        Args:
            url (str): A string representing the input Uqload URL.

        Returns:
            str: A validated and formatted Uqload URL.

        Raises:
            ValueError: If the input URL is None, not a string, shorter than 12 characters,
                        or doesn't follow the expected Uqload URL format.
        """
        # Check if the input URL is a string and has a minimum length of 12 characters
        if url is None or not isinstance(url, str) or len(url) < 12:
            raise ValueError("Invalid Uqload URL. Please try again.")

        # Split the URL into two parts: base URL and video ID
        list_of_url = url.rsplit("/", 1)

        # Extract base URL from the split parts, or use a default if no base URL is present
        base_url = list_of_url[0] if len(list_of_url) == 2 else "https://uqload.io"
        video_id = list_of_url[-1]

        # Add ".html" to the video ID if it's not already present
        video_id = f"{video_id}.html" if ".html" not in video_id else video_id
        # Add "embed-" to the video ID if it's not already present
        video_id = f"embed-{video_id}" if "embed-" not in video_id else video_id

        full_url = f"{base_url}/{video_id}"

        # Check if the full URL is a valid Uqload URL
        if not is_uqload_url(full_url):
            raise ValueError("Invalid Uqload URL. Please try again.")

        return full_url

    def __get_video(self) -> None:
        """
        It makes requests to Uqload to obtain information from the video by web scraping.

        Raises:
            ValueError: Any request was unsuccessful.
            VideoNotFound: The video was not found.
        """
        print(f"Looking for video...")

        # Makes two requests to:
        # https://uqload.io/xxxxxxxxxxxx.html and https://uqload.io/embed-xxxxxxxxxxxx.html
        urls_to_fetch = [self.url, self.url.replace("embed-", "")]
        self.url_fetcher = URLFetcher(urls_to_fetch)
        responses = self.url_fetcher.start()

        # Checking if responses are valid
        if responses[0] is None or responses[1] is None:
            raise ValueError("No content")

        # Handling case when the video has been deleted or does not exist
        if "File was deleted" in responses[0].text:
            raise VideoNotFound("The video has been deleted or does not exist")

        response_text_0 = responses[0].text
        response_text_1 = responses[1].text
        video_url = re.findall(r"https?://.+/v\.mp4", response_text_0)
        if not len(video_url):
            raise VideoNotFound("The video has been deleted or does not exist")

        # Extracting video URL, image URL, and title using regex
        video_url = str(video_url[0])
        image_url = str(re.findall(r"https?://.*?\.jpg", response_text_0)[0])
        title = str(re.findall(r'title:\s*"([^"]+)"', response_text_0)[0])

        # NOTE: sometimes the duration and resolution may not be available.
        resolution = None
        duration = None
        # Extracting class names for additional video info (title, duration, resolution)
        class_names = re.findall(r'class\s*=\s*[\'"]([^\'" ]+)[\'"]', response_text_1)
        # Parsing additional video info if "err" class is not present
        if not "err" in class_names:
            # extracts the title from the home page
            # sometimes the title is different from the one in the embedded mode
            h1_tag = re.findall(r"<h1[^>]*>(.*?)</h1>", response_text_1, re.DOTALL)
            if len(h1_tag):
                title = remove_special_characters(" ".join(str(h1_tag[0]).split()))

            # Use regular expression to find textarea
            textarea_content = re.findall(
                r"<textarea[^>]*>(.*?)</textarea>", response_text_1, re.DOTALL
            )
            # Extracts the length of the video
            resolution_pattern = r"\[(\d+x\d+)\, ((\d+:)*\d+)\]"
            for textarea in textarea_content:
                matches = re.search(resolution_pattern, textarea)
                if matches:
                    resolution = matches.group(1)
                    duration = matches.group(2)
                    break

        # Sanitizing title and assigning output file name if not provided
        new_title = remove_special_characters(title)
        if self.output_file is None:
            self.output_file = new_title if len(new_title) else uuid4().hex

        # Initiating FileDownloader instance for video download
        self.__downloader = FileDownloader(
            url=video_url,
            filename=self.output_file,
            output_dir=self.output_dir,
            on_progress_callback=self.on_progress_callback,
        )

        # Storing video information in a dictionary
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
        Retrieves video information.

        Returns:
            dict: Returns a dictionary with the video information.
        """
        if not len(self.__video_info):
            self.__get_video()
        return self.__video_info

    def download(self) -> None:
        """Downloads the video."""
        if not len(self.__video_info):
            self.__get_video()
        self.__downloader.download()
