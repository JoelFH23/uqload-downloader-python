# Uqload Downloader Python

You can download any video from Uqload. You only need the URL of the video.

Inspired by [thomasarmel/uqload_downloader](https://github.com/thomasarmel/uqload_downloader)

[GUI version](https://github.com/JoelFH23/uqload-downloader-gui)

---

## Requirements

-   Python 3.9 or greater.

## Installation

### From PyPI

You can install the package directly from PyPI using pip:

```bash
python -m pip install uqload-dl==1.0
```

### From Source Code

1. Clone the repository:

```bash
git clone https://github.com/JoelFH23/uqload-downloader-python
```

2. Navigate to the package directory:

```bash
cd uqload-downloader-python
```

3. Install the package:

```bash
python -m pip install .
```

Alternatively, you can install it in development mode to easily make changes:

```bash
python -m pip install -e .
```

### Directly from GitHub

You can install the package directly from GitHub using pip:

```bash
python -m pip install git+https://github.com/JoelFH23/uqload-downloader-python
```

## Usage

### Using the CLI

To download a video

```bash
uqload_dl -u https://uqload.io/xxxxxxxxxxxx.html
```

You can specify a video name using "-n" or "--name"

```bash
uqload_dl -u https://uqload.io/xxxxxxxxxxxx.html -n "The best video"
```

if no name is specified, the original name of the video will be used.

You can specify the path where the video will be stored using "-o" or "--outdir"

```bash
uqload_dl -u https://uqload.io/xxxxxxxxxxxx.html -n "The best video" -o C:\\Users\\Joel\\Desktop\\My Videos
```

if no path is specified, the current working path will be used.

### Using a Python Script

```Python
from uqload_dl import UQLoad
uqload = UQLoad(url="https://uqload.io/xxxxxxxxxxxx.html",output_file="The best video")
uqload.download() # download the video
```

### Example Usage

```bash
(python3.9) PS C:\Users\Joel\desktop> uqload_dl -u vule3vel9n5q
Looking for video...
------------------------------------------------------------
                video info
------------------------------------------------------------
url : https://m180.uqload.io/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6j6f5krce4q/v.mp4
title : python testing time
image_url : https://m180.uqload.io/i/05/02288/vule3vel9n5q_xt.jpg
resolution : 860x360
duration : 00:22
size : 915562 bytes
type : video/mp4
------------------------------------------------------------
Do you want to download the video? (yes/[no]):
```

Note: sometimes the resolution and duration will not be available.

You can use "-y" or "--yes" to start the download automatically.

```bash
(python3.9) PS C:\Users\Joel\desktop> uqload_dl -u vule3vel9n5q -y
Looking for video...
------------------------------------------------------------
                video info
------------------------------------------------------------
url : https://m180.uqload.io/3rfkv4rhrvw2q4drdkgpxmnva6flydhkehdqtxrb6635d6s4w6jydssrce4q/v.mp4
title : python testing time
image_url : https://m180.uqload.io/i/05/02288/vule3vel9n5q_xt.jpg
resolution : 860x360
duration : 00:22
size : 915562 bytes
type : video/mp4
------------------------------------------------------------
Downloading... |----------------------------------------| 100.00% completed
Video saved as: C:\Users\Joel\desktop\python testing time.mp4
```

## License

Licensed under the [GPLv3](https://choosealicense.com/licenses/gpl-3.0/).
