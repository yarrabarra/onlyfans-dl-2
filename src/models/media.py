from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field
from urllib.parse import urlencode


class PreviewUrl(BaseModel):
    url: str


class Video(BaseModel):
    mp4: str


class Manifest(BaseModel):
    hls: str
    dash: str


class Hls(BaseModel):
    CloudFront_Policy: str = Field(..., alias="CloudFront-Policy")
    CloudFront_Signature: str = Field(..., alias="CloudFront-Signature")
    CloudFront_Key_Pair_Id: str = Field(..., alias="CloudFront-Key-Pair-Id")


class Dash(BaseModel):
    CloudFront_Policy: str = Field(..., alias="CloudFront-Policy")
    CloudFront_Signature: str = Field(..., alias="CloudFront-Signature")
    CloudFront_Key_Pair_Id: str = Field(..., alias="CloudFront-Key-Pair-Id")


class Signature(BaseModel):
    hls: Hls
    dash: Dash


class Drm(BaseModel):
    manifest: Manifest
    signature: Signature


class Files(BaseModel):
    preview: Optional[PreviewUrl] = None
    source: Optional[PreviewUrl] = None
    drm: Optional[Drm] = None


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

    def _get_drm_url(self):
        if self.files is None or self.files.drm is None:
            return None
        params = urlencode(
            {
                "Tag": 2,
                "Policy": self.files.drm.signature.dash.CloudFront_Policy,
                "Signature": self.files.drm.signature.dash.CloudFront_Signature,
                "Key-Pair-Id": self.files.drm.signature.dash.CloudFront_Key_Pair_Id,
            }
        )
        return f"{self.files.drm.manifest.dash}?{params}"

    def is_downloadable(self):
        if self.type not in ("photo", "video", "audio"):
            return False
        return self.canView

    def is_drm(self):
        if self.files is None:
            return False
        if self.files.drm is None:
            return False
        return True

    def get_source(self) -> Optional[str]:
        if self.source.source is not None:
            return self.source.source
        if self.files is None:
            return None
        if self.is_drm():
            return self._get_drm_url()
        if self.files.source is None:
            return None
        if self.files.source.url is not None:
            return self.files.source.url
        return None
