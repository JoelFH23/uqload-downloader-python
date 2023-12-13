import pytest, sys, os
from io import StringIO
from uqload_dl.cli import main, print_video_info


@pytest.mark.parametrize("value", [(None), (True), ({}), (1), ("test"), ("")])
def test_invalid_video_info(value) -> None:
    with pytest.raises(ValueError):
        print_video_info(value)


def test_print_video_info_output(capsys) -> None:
    video_info = {
        "title": "Sample Video",
        "duration": "10:30",
        "size": "1234567890",
        "type": "video/mp4",
    }

    expected_output = (
        "------------------------------------------------------------\n"
        "\t\tvideo info\n"
        "------------------------------------------------------------\n"
        "title : Sample Video\n"
        "duration : 10:30\n"
        "size : 1234567890 bytes\n"
        "type : video/mp4\n"
        "------------------------------------------------------------\n"
    )

    print_video_info(video_info)
    out, _ = capsys.readouterr()
    assert out == expected_output


def test_video_download_cancelled(monkeypatch, capsys) -> None:
    # Mocking user input to simulate cancellation
    input_mock = StringIO("no\n")
    monkeypatch.setattr("sys.stdin", input_mock)

    # Simulating CLI arguments
    sys.argv = ["", "--url", "vule3vel9n5q"]

    main()
    out, _ = capsys.readouterr()
    assert "The download has been cancelled" in out


def test_main_user_input_yes(monkeypatch, capsys) -> None:
    # Simulating user input 'yes' to download the video
    input_mock = StringIO("yes\n")
    monkeypatch.setattr("sys.stdin", input_mock)

    # Simulating CLI arguments
    sys.argv = ["", "--url", "vule3vel9n5q"]

    main()
    out, _ = capsys.readouterr()
    assert "The video has been downloaded successfully" in out

    for item in os.listdir(os.getcwd()):
        if item.endswith(".mp4"):
            os.remove(item)
