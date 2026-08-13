from dataclasses import dataclass


@dataclass(frozen=True)
class VideoQuality:
    url: str
    resolution: str
    size: str


@dataclass(frozen=True)
class VideoInfo:
    title: str
    duration: str
    mp4_url: str
    resolution: str
    file_size: int
