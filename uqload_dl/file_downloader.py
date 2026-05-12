import re, os, urllib
from uqload_dl.utils import is_a_callback, is_a_valid_directory, validate_output_file
from uqload_dl.parallel_downloader import ParallelDownloader
from urllib.parse import urlparse
from typing import Callable
from uuid import uuid4

# Test: https://sampletestfile.com/wp-content/uploads/2023/07/15MB-MP4.mp4

# ANSI color codes for better UI
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
        # Optimisation ULTRA: Chunk size optimisé pour vitesse ULTRA
        self.chunk_size = 10 * 1024 * 1024  # 10MB chunks pour vitesse ULTRA
        self.progress_update_interval = 1024 * 1024  # Mise à jour progrès tous les 1MB pour voir l'avancée

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
            "Accept-Encoding": "identity",  # Pas de compression pour éviter overhead
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=1200, max=5000",
            "Range": "bytes=0-",  # Support pour les reprises de téléchargement
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "DNT": "1"
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
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.getcode() not in [200, 206]:
                    raise ValueError("Received non-200/206 HTTP response")

                self.total_size = int(response.info().get("Content-Length", 0))

                if not self.total_size:
                    raise ValueError("Missing Content-Length in response")

                self.type = response.info().get("Content-Type", "")
        except urllib.error.HTTPError as e:
            raise ValueError(f"FileDownloader HTTPError {self.url}: {e}") from e
        except urllib.error.URLError as e:
            raise ValueError(f"FileDownloader URLError {self.url}: {e}") from e
        except Exception as e:
            raise ValueError(f"FileDownloader Unexpected error {self.url}: {e}") from e

    @property
    def filename(self) -> str:
        """Returns the output filename."""
        return self.__filename

    def delete_file(self) -> None:
        """Deletes the downloaded file if it exists."""
        if os.path.exists(self.destination):
            print(f"{Colors.WARNING}🗑️  Deleted: {self.destination}{Colors.ENDC}")
            os.remove(self.destination)

    def download(self) -> None:
        """
        Downloads the file from the URL using parallel segments for maximum speed.

        Raises:
            ValueError: If the file cannot be downloaded.
            KeyboardInterrupt: If interrupted by user.
            Exception: For other errors.
        """
        try:
            filename = f"{self.__filename}{self.__extension}"
            
            # Utiliser le téléchargeur parallèle pour vitesse maximale
            if self.total_size > 1 * 1024 * 1024:  # > 1MB, utiliser téléchargement parallèle
                import multiprocessing
                cpu_count = multiprocessing.cpu_count()
                optimal_segments = min(16, cpu_count * 2)  # Utilise 2x le nombre de CPU
                
                print(f"🚀 Téléchargement par segments parallèles ({optimal_segments} connexions)")
                parallel_downloader = ParallelDownloader(
                    url=self.url,
                    filename=filename,
                    output_dir=self.output_dir,
                    total_size=self.total_size,
                    headers=self.headers,
                    on_progress_callback=self.on_progress_callback,
                    num_segments=optimal_segments  # Segments optimaux basés sur CPU
                )
                
                self.destination = parallel_downloader.download()
            else:
                # Téléchargement normal pour petits fichiers
                print(f"📥 Téléchargement normal (fichier < 1MB)")
                self._download_normal(filename)
                
            # Finish the progress bar
            if self.on_progress_callback:
                from uqload_dl.progress_bar import ProgressBar
                if isinstance(self.on_progress_callback, ProgressBar):
                    self.on_progress_callback.finish()
            
            print(f"\n{Colors.OKGREEN}💾 File saved as: {Colors.BOLD}{self.destination}{Colors.ENDC}")

        except urllib.error.HTTPError as error:
            print(f"\n{Colors.FAIL}❌ HTTP ERROR: {str(error)}{Colors.ENDC}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Download cancelled by user.{Colors.ENDC}")
        except Exception as ex:
            print(f"\n{Colors.FAIL}❌ Unexpected error: {ex}{Colors.ENDC}")
    
    def _download_normal(self, filename: str) -> None:
        """Téléchargement normal (fallback pour petits fichiers)."""
        request = urllib.request.Request(self.url, headers=self.headers)
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.getcode() not in [200, 206]:
                raise ValueError("file cannot be downloaded")

            self.destination = os.path.join(self.output_dir, filename)

            # Avoid overwrite
            if os.path.isfile(self.destination):
                base, ext = os.path.splitext(filename)
                self.destination = os.path.join(
                    self.output_dir, f"{base}_{uuid4().hex}{ext}"
                )

            # Optimisation vitesse: buffer plus grand et mise à jour moins fréquente
            last_progress_update = 0
            with open(self.destination, "wb", buffering=self.chunk_size) as file:
                while chunk := response.read(self.chunk_size):
                    file.write(chunk)
                    self.bytes_downloaded += len(chunk)
                    
                    # Mise à jour du progrès moins fréquente pour performance
                    if (self.on_progress_callback and 
                        self.bytes_downloaded - last_progress_update >= self.progress_update_interval):
                        self.on_progress_callback(
                            self.bytes_downloaded, self.total_size
                        )
                        last_progress_update = self.bytes_downloaded
