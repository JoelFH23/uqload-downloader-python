import argparse
import sys
import os
from uqload_dl.progress_bar import ProgressBar
from uqload_dl.version import __version__
from uqload_dl.uqload import UQLoad
from uqload_dl.batch_downloader import BatchDownloader
from typing import Dict
from uqload_dl.utils import sizeof_fmt


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


def print_header():
    """Print the application header."""
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    UQLOAD DOWNLOADER                        ║")
    print("║                     Fast & Efficient                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")


def print_video_info(video_info: Dict[str, str]) -> None:
    """
    Prints video information with improved formatting.

    Args:
        video_info (dict): Video information.

    Raises:
        ValueError: if video_info is not dictionary.
    """
    if video_info is None or not isinstance(video_info, dict) or not len(video_info):
        raise ValueError("video_info must be a dictionary")

    print(f"\n{Colors.OKBLUE}{Colors.BOLD}📹 VIDEO INFORMATION{Colors.ENDC}")
    print("═" * 60)

    # Define display order and icons
    display_order = [
        ('title', '📝 Title'),
        ('resolution', '🖥️  Resolution'),
        ('duration', '⏱️  Duration'),
        ('size', '💾 Size'),
        ('type', '🎬 Type'),
        ('url', '🔗 URL')
    ]

    for key, label in display_order:
        if key in video_info and video_info[key]:
            value = video_info[key]
            if key == "size":
                formatted_value = sizeof_fmt(value)
                print(f"{Colors.OKCYAN}{label:<15}{Colors.ENDC}: {Colors.BOLD}{formatted_value}{Colors.ENDC}")
            else:
                print(f"{Colors.OKCYAN}{label:<15}{Colors.ENDC}: {Colors.BOLD}{value}{Colors.ENDC}")

    print("═" * 60)


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


def get_default_download_dir():
    """Get the default download directory (Desktop)."""
    desktop = os.path.expanduser("~/Desktop")
    # Create Desktop directory if it doesn't exist
    os.makedirs(desktop, exist_ok=True)
    return desktop


def interactive_url_input():
    """Ask user for URL interactively."""
    print(f"\n{Colors.OKCYAN}🔗 Please enter the Uqload URL:{Colors.ENDC}")
    while True:
        url = input(f"{Colors.BOLD}URL: {Colors.ENDC}").strip()
        if url:
            return url
        else:
            print(f"{Colors.WARNING}⚠️  Please enter a valid URL{Colors.ENDC}")


def main() -> None:
    """Main function with improved interface."""
    print_header()
    
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}Simple and fast script to download videos from Uqload{Colors.ENDC}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.OKCYAN}Examples:{Colors.ENDC}
  Interactive mode (recommended):
    uqload-dl
    uqload-dl -y

  Single video download:
    uqload-dl -u https://uqload.is/sbmujieyd2cj.html
    uqload-dl -u https://uqload.is/sbmujieyd2cj.html -o /downloads -y

  Batch download from file:
    uqload-dl -f urls.txt
    uqload-dl -f urls.txt -o /downloads -w 5

{Colors.WARNING}File format for batch download:{Colors.ENDC}
  Create a text file with one URL per line, starting with @:
  @https://uqload.is/sbmujieyd2cj.html
  @https://uqload.is/another-video.html
        """
    )
    
    # Create mutually exclusive group for URL vs file input
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument("-u", "--url", help="The URL or ID of the video to download")
    input_group.add_argument("-f", "--file", help="Text file containing URLs to download (format: @url per line)")
    
    parser.add_argument("-o", "--outdir", help="Folder where the file(s) will be saved")
    parser.add_argument("-n", "--name", help="Video name (only for single URL download)")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Download the video automatically without confirmation",
    )
    parser.add_argument(
        "-w", 
        "--workers", 
        type=int, 
        default=16, 
        help="Number of concurrent downloads (default: 16, only for batch downloads)"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"{Colors.OKGREEN}%(prog)s {__version__}{Colors.ENDC}"
    )

    args = parser.parse_args()

    try:
        # Set default output directory to Desktop
        output_dir = args.outdir or get_default_download_dir()
        
        # Handle batch download from file
        if args.file:
            print_info(f"Starting batch download from file: {Colors.BOLD}{args.file}{Colors.ENDC}")
            print_info(f"Output directory: {Colors.BOLD}{output_dir}{Colors.ENDC}")
            print_info(f"Concurrent downloads: {Colors.BOLD}{args.workers}{Colors.ENDC}")
            print()
            
            batch_downloader = BatchDownloader(
                max_workers=args.workers,
                output_dir=output_dir,
                on_progress_callback=lambda downloaded, total: ProgressBar(total).update(downloaded)
            )
            
            results = batch_downloader.download_from_file(args.file)
            
            successful = len([r for r in results if r['success']])
            total = len(results)
            
            print()
            if successful == total:
                print_success(f"All {total} videos downloaded successfully! 🎉")
            else:
                print_warning(f"{successful}/{total} videos downloaded successfully.")
                
        # Handle single URL download (interactive or direct)
        elif args.url:
            print_info(f"Processing URL: {Colors.BOLD}{args.url}{Colors.ENDC}")
            print_info(f"Output directory: {Colors.BOLD}{output_dir}{Colors.ENDC}")
            if args.name:
                print_info(f"Custom filename: {Colors.BOLD}{args.name}{Colors.ENDC}")
            print()
            
            uqload_instance = UQLoad(
                url=args.url,
                output_file=args.name,
                output_dir=output_dir,
                on_progress_callback=lambda downloaded, total: ProgressBar(
                    total
                ).update(downloaded),
            )

            print_video_info(uqload_instance.get_video_info())
            print()

            if not args.yes:
                print(f"{Colors.WARNING}Do you want to download this video?{Colors.ENDC}")
                a = input(f"{Colors.OKCYAN}Type 'yes' or 'y' to continue: {Colors.ENDC}")
                if a.lower() in ['yes', 'y']:
                    print()
                    uqload_instance.download()
                    print_success("Video downloaded successfully!")
                else:
                    print_warning("Download cancelled by user.")
            else:
                print()
                uqload_instance.download()
                print_success("Video downloaded successfully!")
        
        # Interactive mode - no URL or file provided
        else:
            print_info(f"Welcome to interactive mode! 🎉")
            print_info(f"Default download directory: {Colors.BOLD}{output_dir}{Colors.ENDC}")
            print()
            
            # Ask for URL interactively
            url = interactive_url_input()
            
            print_info(f"Processing URL: {Colors.BOLD}{url}{Colors.ENDC}")
            print_info(f"Output directory: {Colors.BOLD}{output_dir}{Colors.ENDC}")
            print()
            
            uqload_instance = UQLoad(
                url=url,
                output_file=args.name,
                output_dir=output_dir,
                on_progress_callback=lambda downloaded, total: ProgressBar(
                    total
                ).update(downloaded),
            )

            print_video_info(uqload_instance.get_video_info())
            print()

            if not args.yes:
                print(f"{Colors.WARNING}Do you want to download this video?{Colors.ENDC}")
                a = input(f"{Colors.OKCYAN}Type 'yes' or 'y' to continue: {Colors.ENDC}")
                if a.lower() in ['yes', 'y']:
                    print()
                    uqload_instance.download()
                    print_success("Video downloaded successfully!")
                else:
                    print_warning("Download cancelled by user.")
            else:
                print()
                uqload_instance.download()
                print_success("Video downloaded successfully!")
                
    except KeyboardInterrupt:
        print()
        print_warning("Operation cancelled by user.")
        sys.exit(1)
    except Exception as ex:
        print_error(str(ex))
        sys.exit(1)


if __name__ == "__main__":
    main()

# https://uqload.is/embed-0zmi1ulf0d60.html
# https://uqload.is/embed-h63yfu9dkw1r.html
# https://uqload.is/vule3vel9n5q.html
