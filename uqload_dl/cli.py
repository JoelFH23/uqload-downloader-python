import argparse
import sys

from uqload_dl.version import __version__
from uqload_dl.uqload import UQload
from uqload_dl.utils import format_size

from uqload_dl.models import VideoInfo

# https://uqload.is/2opgl0kx82bd.html
# https://uqload.is/00de21ob60k9.html


def print_progress_bar(downloaded: int, total: int, bar_length: int = 30):
    if total <= 0:
        downloaded_mb = downloaded / (1024 * 1024)
        sys.stdout.write(f"\rDownloading... {downloaded_mb:.2f} MB")
        sys.stdout.flush()
        return
    percent = min(downloaded / total, 1.0)
    filled_length = int(bar_length * percent)

    bar = "█" * filled_length + "░" * (bar_length - filled_length)

    downloaded_mb = downloaded / (1024 * 1024)
    total_mb = total / (1024 * 1024)

    sys.stdout.write(
        f"\r[{bar}] {percent * 100:.2f}% ({downloaded_mb:.2f} MB / {total_mb:.2f} MB)"
    )
    sys.stdout.flush()


def print_video_info(video_info: VideoInfo) -> None:
    bar_length = 50
    print("\n" + "=" * bar_length)
    print("\t\tVIDEO INFO")
    print("=" * bar_length)
    print(f" • Title: {video_info.title}")
    print(f" • Duration: {video_info.duration}")
    print(f" • resolution: {video_info.resolution}")
    print(f" • size: {format_size(video_info.file_size)}")
    print(f" • URL: {video_info.mp4_url}")
    print("=" * bar_length + "\n")


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Simple script to download video from Uqload"
    )
    parser.add_argument("-u", "--url", required=True, help="The video URL")
    parser.add_argument("-o", "--outdir", help="Folder where the file will be saved")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Download the video automatically",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + __version__
    )

    args = parser.parse_args()

    try:
        if args.url:
            print(f"Looking for video...")
            client = UQload(args.outdir if args.outdir else "")
            video_info = client.get_info(args.url)

            print_video_info(video_info)

            if not args.yes:
                a = input(f"Do you want to download the video? (yes/[no]): ")
                if a.lower() == "yes" or a.lower() == "y":
                    client.download(video_info, print_progress_bar)
                    print("The video has been downloaded successfully")
                else:
                    print(f"The download has been cancelled")
            else:
                client.download(video_info, print_progress_bar)
                print("The video has been downloaded successfully")
        else:
            print("No action specified. Use -h or --help for available options.")
    except Exception as ex:
        print(str(ex).upper())


if __name__ == "__main__":
    main()
