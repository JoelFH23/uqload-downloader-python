import pytest, sys, os, builtins
from io import StringIO
from uqload_dl.cli import main, print_video_info
from unittest.mock import patch, MagicMock


def test_print_video_info_invalid_type() -> None:
    with pytest.raises(ValueError):
        print_video_info("not_a_dict")

    with pytest.raises(ValueError):
        print_video_info(None)

    with pytest.raises(ValueError):
        print_video_info({})


def test_print_video_info_valid_output(capsys: pytest.CaptureFixture[builtins.str]):
    info = {
        "title": "Test Video",
        "url": "https://video.com/v.mp4",
        "size": 1048576,
        "resolution": "1920x1080",
        "duration": "01:23",
    }
    print_video_info(info)
    captured = capsys.readouterr()
    assert "Test Video" in captured.out
    assert "1.0 MiB" in captured.out
    assert "video info" in captured.out
