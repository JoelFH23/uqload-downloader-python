import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Callable
from uqload_dl.uqload import UQLoad
from uqload_dl.exceptions import VideoNotFound
from uqload_dl.progress_bar import ProgressBar


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


def get_default_download_dir():
    """Get the default download directory (Desktop)."""
    desktop = os.path.expanduser("~/Desktop")
    # Create Desktop directory if it doesn't exist
    os.makedirs(desktop, exist_ok=True)
    return desktop


class BatchDownloader:
    """
    Handles batch downloading of multiple videos from a text file or list of URLs.
    
    Args:
        max_workers (int): Maximum number of concurrent downloads (default: 16)
        output_dir (str): Directory where files will be saved
        on_progress_callback (Callable): Callback for progress reporting
    """
    
    def __init__(
        self,
        max_workers: int = 16,
        output_dir: str = None,
        on_progress_callback: Callable = None,
    ) -> None:
        self.max_workers = max_workers
        self.output_dir = output_dir or get_default_download_dir()
        self.on_progress_callback = on_progress_callback
        self.results: List[Dict] = []
        
    def read_urls_from_file(self, file_path: str) -> List[str]:
        """
        Reads URLs from a text file.
        
        Expected format:
        @https://uqload.cx/sbmujieyd2cj.html
        @https://uqload.cx/another-video.html
        
        Args:
            file_path (str): Path to the text file containing URLs
            
        Returns:
            List[str]: List of cleaned URLs
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is empty or contains no valid URLs
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Extract URLs starting with @
        urls = re.findall(r'@(https?://[^\s\n]+)', content)
        
        if not urls:
            raise ValueError("No valid URLs found in the file")
            
        # Clean URLs (remove trailing whitespace, etc.)
        cleaned_urls = [url.strip() for url in urls if url.strip()]
        
        if not cleaned_urls:
            raise ValueError("No valid URLs found after cleaning")
            
        return cleaned_urls
    
    def download_single_video(self, url: str, index: int, total: int) -> Dict:
        """
        Downloads a single video.
        
        Args:
            url (str): The video URL to download
            index (int): Current video index (for progress display)
            total (int): Total number of videos
            
        Returns:
            Dict: Result information about the download
        """
        result = {
            'url': url,
            'index': index,
            'success': False,
            'error': None,
            'filename': None
        }
        
        try:
            print(f"\n{Colors.OKBLUE}[{index}/{total}]{Colors.ENDC} {Colors.BOLD}Processing:{Colors.ENDC} {url}")
            
            # Create UQLoad instance
            uqload = UQLoad(
                url=url,
                output_dir=self.output_dir,
                on_progress_callback=self.on_progress_callback
            )
            
            # Get video info
            video_info = uqload.get_video_info()
            title = video_info.get('title', 'Unknown')
            size = video_info.get('size', 0)
            
            print(f"{Colors.OKCYAN}📝 Title:{Colors.ENDC} {Colors.BOLD}{title}{Colors.ENDC}")
            if size:
                from uqload_dl.utils import sizeof_fmt
                print(f"{Colors.OKCYAN}💾 Size:{Colors.ENDC} {Colors.BOLD}{sizeof_fmt(size)}{Colors.ENDC}")
            
            # Download the video
            uqload.download()
            
            result['success'] = True
            result['filename'] = title
            result['size'] = size
            
            print(f"{Colors.OKGREEN}[{index}/{total}] ✅ Successfully downloaded:{Colors.ENDC} {Colors.BOLD}{title}{Colors.ENDC}")
            
        except VideoNotFound as e:
            result['error'] = f"Video not found: {str(e)}"
            print(f"{Colors.FAIL}[{index}/{total}] ❌ Video not found:{Colors.ENDC} {url}")
        except Exception as e:
            result['error'] = str(e)
            print(f"{Colors.FAIL}[{index}/{total}] ❌ Error downloading {url}:{Colors.ENDC} {str(e)}")
            
        return result
    
    def download_from_file(self, file_path: str) -> List[Dict]:
        """
        Downloads all videos from URLs listed in a text file.
        
        Args:
            file_path (str): Path to the text file containing URLs
            
        Returns:
            List[Dict]: List of download results
        """
        urls = self.read_urls_from_file(file_path)
        return self.download_urls(urls)
    
    def download_urls(self, urls: List[str]) -> List[Dict]:
        """
        Downloads multiple videos from a list of URLs.
        
        Args:
            urls (List[str]): List of video URLs to download
            
        Returns:
            List[Dict]: List of download results
        """
        if not urls:
            raise ValueError("No URLs provided")
            
        print(f"\n{Colors.HEADER}{Colors.BOLD}🚀 STARTING BATCH DOWNLOAD{Colors.ENDC}")
        print("═" * 60)
        print(f"{Colors.OKCYAN}📁 Output directory:{Colors.ENDC} {Colors.BOLD}{self.output_dir}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}🔗 Total URLs:{Colors.ENDC} {Colors.BOLD}{len(urls)}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}⚡ Concurrent downloads:{Colors.ENDC} {Colors.BOLD}{self.max_workers}{Colors.ENDC}")
        print("═" * 60)
        
        self.results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_url = {
                executor.submit(self.download_single_video, url, i+1, len(urls)): url
                for i, url in enumerate(urls)
            }
            
            # Process completed downloads
            for future in as_completed(future_to_url):
                result = future.result()
                self.results.append(result)
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _print_summary(self) -> None:
        """Prints a summary of the batch download results."""
        if not self.results:
            return
            
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        print(f"\n{Colors.HEADER}{Colors.BOLD}📊 BATCH DOWNLOAD SUMMARY{Colors.ENDC}")
        print("═" * 60)
        print(f"{Colors.OKCYAN}📈 Total videos:{Colors.ENDC} {Colors.BOLD}{len(self.results)}{Colors.ENDC}")
        print(f"{Colors.OKGREEN}✅ Successful:{Colors.ENDC} {Colors.BOLD}{len(successful)}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ Failed:{Colors.ENDC} {Colors.BOLD}{len(failed)}{Colors.ENDC}")
        
        if successful:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 Successfully downloaded:{Colors.ENDC}")
            for result in successful:
                filename = result['filename'] or 'Unknown'
                size = result.get('size', 0)
                if size:
                    from uqload_dl.utils import sizeof_fmt
                    size_str = sizeof_fmt(size)
                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {Colors.BOLD}{filename}{Colors.ENDC} ({size_str})")
                else:
                    print(f"  {Colors.OKGREEN}✓{Colors.ENDC} {Colors.BOLD}{filename}{Colors.ENDC}")
        
        if failed:
            print(f"\n{Colors.FAIL}{Colors.BOLD}💥 Failed downloads:{Colors.ENDC}")
            for result in failed:
                print(f"  {Colors.FAIL}✗{Colors.ENDC} {result['url']} - {result['error']}")
        
        print("═" * 60)
        
        # Final status message
        if len(successful) == len(self.results):
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎊 All downloads completed successfully!{Colors.ENDC}")
        elif len(successful) > 0:
            print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  {len(successful)}/{len(self.results)} downloads completed successfully.{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}💔 All downloads failed.{Colors.ENDC}")
