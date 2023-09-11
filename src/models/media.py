from pydantic import BaseModel, Field

from typing import Any, Optional
from datetime import datetime


class PreviewUrl(BaseModel):
    url: str


class Video(BaseModel):
    mp4: str


class Files(BaseModel):
    preview: Optional[PreviewUrl] = None
    source: Optional[PreviewUrl] = None


class VideoSources(BaseModel):
    field_720: Any = Field(..., alias="720")
    field_240: Any = Field(..., alias="240")


class Source(BaseModel):
    height: Optional[int] = None
    size: Optional[int] = None
    width: Optional[int] = None
    duration: Optional[int] = None
    source: Optional[str] = None


class Preview(BaseModel):
    width: int
    height: int
    size: int


class Info(BaseModel):
    source: Source
    preview: Preview


class MediaItem(BaseModel):
    id: int
    canView: bool
    convertedToVideo: Optional[bool] = None
    createdAt: Optional[datetime] = None
    duration: Optional[int] = None
    files: Optional[Files] = None
    full: Optional[str] = None
    hasError: bool
    info: Info
    locked: Optional[Any] = None
    preview: Optional[str] = None
    source: Source
    squarePreview: Optional[str] = None
    src: Optional[str] = None
    thumb: Optional[str] = None
    type: str
    video: Optional[Video] = None
    videoSources: VideoSources

    def is_downloadable(self):
        if self.type not in ("photo", "video", "audio"):
            return False
        return self.canView

    def get_source(self) -> Optional[str]:
        if self.source.source is not None:
            return self.source.source
        if self.files is None:
            return None
        if self.files.source is None:
            return None
        if self.files.source.url is not None:
            return self.files.source.url
        return None
