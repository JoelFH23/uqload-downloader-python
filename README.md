# Uqload Downloader Python

You can download any video from Uqload. You only need the URL of the video.

Inspired by [thomasarmel/uqload_downloader](https://github.com/thomasarmel/uqload_downloader)

---

## Requirements

-   Python 3.9 or higher

Make sure that you have all of the required dependencies installed before running the script. You can install the required dependencies by running the following command:

```python
pip install -r requirements.txt
```

## Usage

#### Download a video

```python
python main.py --url "https://uqload.co/embed-xxxxxxxxxxxx.html" --name "My video"
```

If no video name is specified, the current date will be used as the video name.

The downloaded videos will be saved in the "videos" folder.

Note: If you press Ctrl+C while downloading a video, it will be automatically deleted.
