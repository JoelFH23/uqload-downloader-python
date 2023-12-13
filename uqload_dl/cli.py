import argparse
from uqload_dl.progress_bar import ProgressBar
from uqload_dl.version import __version__
from uqload_dl.uqload import UQLoad
from typing import Dict


def print_video_info(video_info: Dict[str, str]) -> None:
    """
    Prints video information.

    Args:
        video_info (dict): Video information.

    Raises:
        ValueError: if video_info is not dictionary.
    """
    if video_info is None or not isinstance(video_info, dict) or not len(video_info):
        raise ValueError("video_info must be a dictionary")

    bar_length = 60
    print("-" * bar_length)
    print("\t\tvideo info")
    print("-" * bar_length)

    for key, value in video_info.items():
        row = f"{key} : {value} bytes" if key == "size" else f"{key} : {value}"
        print(f"{row}")

    print("-" * bar_length)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Simple script to download video from Uqload"
    )
    parser.add_argument("-u", "--url", required=True, help="The url or id of the video")
    parser.add_argument("-o", "--outdir", help="Folder where the file will be saved")
    parser.add_argument("-n", "--name", help="Video name")
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

    if args.url:
        uqload_instance = UQLoad(
            url=args.url,
            output_file=args.name,
            output_dir=args.outdir,
            on_progress_callback=lambda downloaded, total: ProgressBar(total).update(
                downloaded
            ),
        )

        print_video_info(uqload_instance.get_video_info())
        print()

        if not args.yes:
            a = input(f"Do you want to download the video? (yes/[no]): ")
            if a.lower() == "yes" or a.lower() == "y":
                uqload_instance.download()
                print("The video has been downloaded successfully")
            else:
                print(f"The download has been cancelled")
        else:
            uqload_instance.download()
            print("The video has been downloaded successfully")
    else:
        print("No action specified. Use -h or --help for available options.")


if __name__ == "__main__":
    main()

# https://uqload.com/embed-0zmi1ulf0d60.html
# https://uqload.com/embed-h63yfu9dkw1r.html
# https://uqload.io/vule3vel9n5q.html"
