from pytest import CaptureFixture, MonkeyPatch

from unittest.mock import MagicMock

from uqload_dl.cli import print_progress_bar, print_video_info, main
from uqload_dl.models import VideoInfo


def test_print_progress_bar(capsys: CaptureFixture[str]) -> None:
    print_progress_bar(50, 100)

    output = capsys.readouterr().out

    assert "50.00%" in output
    assert "0.00 B / 0.00 B" not in output


def test_print_progress_bar_without_total(capsys: CaptureFixture[str]) -> None:
    print_progress_bar(1024 * 1024, 0)

    output = capsys.readouterr().out

    assert "Downloading... 1.00 MB" in output


def test_print_video_info(capsys: CaptureFixture[str]):
    video_info = VideoInfo(
        title="Test Video",
        duration="01:30",
        mp4_url="https://example.com/video.mp4?key=ey",
        resolution="1920x1080",
        file_size=1024 * 1024,
    )

    print_video_info(video_info)

    output = capsys.readouterr().out

    assert "VIDEO INFO" in output
    assert "Test Video" in output
    assert "01:30" in output
    assert "1920x1080" in output
    assert "https://example.com/video.mp4?key=ey" in output
    assert "1.00 MB" in output


def test_main_download_with_yes(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    video_info = VideoInfo(
        title="Test Video",
        duration="01:30",
        mp4_url="https://example.com/video.mp4",
        resolution="1920x1080",
        file_size=1024,
    )

    mock_client = MagicMock()
    mock_client.get_info.return_value = video_info

    monkeypatch.setattr(
        "uqload_dl.cli.UQload",
        lambda output_dir: mock_client,
    )

    monkeypatch.setattr(
        "sys.argv",
        ["uqload-dl", "-u", "https://uqload.io/abc123", "-y"],
    )

    main()

    mock_client.get_info.assert_called_once_with("https://uqload.io/abc123")

    mock_client.download.assert_called_once()

    output = capsys.readouterr().out

    assert "VIDEO INFO" in output
    assert "Test Video" in output
    assert "downloaded successfully" in output


def test_main_download_after_confirmation(monkeypatch: MonkeyPatch) -> None:
    video_info = VideoInfo(
        title="Test Video",
        duration="01:30",
        mp4_url="https://example.com/video.mp4",
        resolution="1920x1080",
        file_size=1024,
    )

    mock_client = MagicMock()
    mock_client.get_info.return_value = video_info

    monkeypatch.setattr(
        "uqload_dl.cli.UQload",
        lambda output_dir: mock_client,
    )

    monkeypatch.setattr(
        "sys.argv",
        ["uqload-dl", "-u", "https://uqload.io/abc123"],
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "yes",
    )

    main()

    mock_client.download.assert_called_once()


def test_main_cancel_download(monkeypatch: MonkeyPatch) -> None:
    video_info = VideoInfo(
        title="Test Video",
        duration="01:30",
        mp4_url="https://example.com/video.mp4",
        resolution="1920x1080",
        file_size=1024,
    )

    mock_client = MagicMock()
    mock_client.get_info.return_value = video_info

    monkeypatch.setattr(
        "uqload_dl.cli.UQload",
        lambda output_dir: mock_client,
    )

    monkeypatch.setattr(
        "sys.argv",
        ["uqload-dl", "-u", "https://uqload.io/abc123"],
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "no",
    )

    main()

    mock_client.download.assert_not_called()
