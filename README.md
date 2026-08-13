# UQload Downloader Python

A lightweight Python library for retrieving video information and downloading videos from UQload.

## Features

- Extract video metadata
- Retrieve direct download URLs
- Download videos with progress callbacks
- Uses only Python's standard library
- No external dependencies

## Installation

### From PyPI

```bash
pip install uqload-dl
```

### From Source

```bash
git clone https://github.com/JoelFH23/uqload-downloader-python.git
cd uqload-downloader-python
python -m pip install .
```

To install with development dependencies (e.g., for testing):
```bash
python -m pip install .[dev]
```


## Quick Start

### Get Video Information

```python
from uqload_dl import UQload

client = UQload()

video = client.get_info(
    "https://uqload.is/embed-xxxxxxxx.html"
)

print(video.title)
print(video.duration)
print(video.resolution)
print(video.file_size)
print(video.mp4_url)
```

Example output:

```text
Title: Example Video
Duration: 00:15:32
Resolution: 1920x1080
File Size: 104857600
MP4 URL: https://...
```

---

### Download a Video

```python
from uqload_dl import UQload

client = UQload()

video = client.get_info(
    "https://uqload.is/embed-xxxxxxxx.html"
)

client.download(video)
```

---

### Download with Progress Tracking

```python
from uqload_dl import UQload


def progress(downloaded: int, total: int) -> None:
    percentage = downloaded / total * 100
    print(f"\r{percentage:.2f}%", end="")


client = UQload()

video = client.get_info(
    "https://uqload.is/embed-xxxxxxxx.html"
)

client.download(
    video_info=video,
    progress_callback=progress,
)
```

## Custom Download Directory

By default, files are downloaded to the user's Downloads directory.

```python
from uqload_dl import UQload

client = UQload(
    output_dir="/home/Joel/Videos"
)
```

### From the command line

```bash
uqload-dl -u "https://uqload.io/xxxxxxxxxxxx.html"
```

#### Optional arguments:
```bash
uqload-dl -u "https://uqload.io/xxxxxxxxxxxx.html" -o /home/joel/Videos
```

## Requirements

- Python 3.10+

## Disclaimer

This project is intended for educational and personal use only.

Users are responsible for ensuring they comply with all applicable laws, website terms of service, and copyright regulations.

## License

This project is licensed under the terms of the **GNU General Public License v3.0**.  
See the [LICENSE](LICENSE) file for full details.