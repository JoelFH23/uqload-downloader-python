# uqload-dl

**Download any video from the UQload site using Python.**

[![PyPI version](https://badge.fury.io/py/uqload-dl.svg)](https://pypi.org/project/uqload-dl)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

---

## Features

- Extract and download videos from UQload
- Custom output filename and directory
- Supports download progress callback
- Simple command-line interface
- Lightweight and dependency-free

---

## Installation

### From PyPI

```bash
pip install uqload-dl
```

### From Source

Clone the repository and install it manually:

```bash
git clone https://github.com/JoelFH23/uqload-downloader-python.git
cd uqload-downloader-python
python -m pip install .
```

To install with development dependencies (e.g., for testing):

```bash
python -m pip install .[dev]
```

## Usage

### As a Python module

```bash
from uqload_dl import UQLoad

video = UQLoad(
    url="https://uqload.io/xxxxxxxxxxxx.html",
    output_file="my_video",
    output_dir="/home/joel/Videos"
)
video.download()
```

#### From the command line

```bash
uqload-dl -u "https://uqload.io/xxxxxxxxxxxx.html"
```

#### Optional arguments:
```bash
uqload-dl -u "https://uqload.io/xxxxxxxxxxxx.html" -n my_video -o /home/joel/Videos
```

---

## GUI Version

If you prefer a graphical interface, check out the GUI version of this project:

➡️ **[uqload-downloader-gui](https://github.com/JoelFH23/uqload-downloader-gui)**  
Built with Python and PyQt for a simple and intuitive user experience.

---

## Requirements

- Python 3.9 or higher
- No external dependencies required

---

## Development

Run tests with:

```bash
pytest
```

---

## License

This project is licensed under the terms of the **GNU General Public License v3.0**.  
See the [LICENSE](LICENSE) file for full details.

---