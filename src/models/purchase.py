from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from .profile import Profile
from .media import MediaItem


class Purchase(BaseModel):
    responseType: str
    text: str
    giphyId: Any
    lockedText: bool
    isFree: bool
    price: float
    isMediaReady: bool
    mediaCount: int
    media: list[MediaItem]
    previews: list[int]
    isTip: bool
    isReportedByMe: bool
    isCouplePeopleMedia: bool
    queueId: int
    fromUser: Profile | None = None
    isFromQueue: bool
    canUnsendQueue: Optional[bool] = None
    unsendSecondsQueue: Optional[int] = None
    id: int
    isOpened: bool
    isNew: bool
    createdAt: datetime | None = None
    changedAt: datetime
    cancelSeconds: int
    isLiked: bool
    canPurchase: bool
    canReport: bool

    def is_viewable(self):
        if self.fromUser is None:
            return False
        return True

    def get_postdate(self):
        if self.createdAt is None:
            return "1970-01-01"  # Epoch failsafe if date is not present
        return self.createdAt.strftime("%Y-%m-%d")
