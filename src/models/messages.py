from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from .media import MediaItem
from .profile import Profile


class Message(BaseModel):
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
    fromUser: Profile
    isFromQueue: bool
    canUnsendQueue: Optional[bool] = None
    unsendSecondsQueue: Optional[int] = None
    id: int
    isOpened: bool
    isNew: bool
    createdAt: datetime
    changedAt: datetime
    cancelSeconds: int
    isLiked: bool
    canPurchase: bool
    canPurchaseReason: str
    canReport: bool
    canBePinned: bool
    isPinned: bool

    def is_viewable(self):
        return True

    def get_postdate(self):
        if self.createdAt is None:
            return "1970-01-01"  # Epoch failsafe if date is not present
        return self.createdAt.strftime("%Y-%m-%d")


class MessageList(BaseModel):
    list: list[Message]
    hasMore: bool
