from datetime import datetime
from typing import Any, Optional
from decimal import Decimal

from pydantic import BaseModel

from .media import MediaItem


class AvatarThumbs(BaseModel):
    c50: str
    c144: str


class HeaderSize(BaseModel):
    width: int
    height: int


class HeaderThumbs(BaseModel):
    w480: str
    w760: str


class SubscriptionBundle(BaseModel):
    id: int
    discount: int
    duration: int
    price: Decimal
    canBuy: bool


class ListsState(BaseModel):
    id: str
    type: str
    name: str
    hasUser: bool
    canAddUser: bool


class FromUser(BaseModel):
    view: str
    avatar: str
    avatarThumbs: AvatarThumbs
    header: str
    headerSize: HeaderSize
    headerThumbs: HeaderThumbs
    id: int
    name: str
    username: str
    canLookStory: bool
    canCommentStory: bool
    hasNotViewedStory: bool
    isVerified: bool
    canPayInternal: bool
    hasScheduledStream: bool
    hasStream: bool
    hasStories: bool
    tipsEnabled: bool
    tipsTextEnabled: bool
    tipsMin: int
    tipsMinInternal: int
    tipsMax: int
    canEarn: bool
    canAddSubscriber: bool
    subscribePrice: Decimal
    subscriptionBundles: list[SubscriptionBundle]
    isPaywallRequired: bool
    unprofitable: bool
    listsStates: list[ListsState]
    isMuted: bool
    isRestricted: bool
    canRestrict: bool
    subscribedBy: bool
    subscribedByExpire: bool
    subscribedByExpireDate: datetime
    subscribedByAutoprolong: bool
    subscribedIsExpiredNow: bool
    currentSubscribePrice: Decimal
    subscribedOn: Any
    subscribedOnExpiredNow: Any
    subscribedOnDuration: Any
    callPrice: Decimal
    lastSeen: str
    canReport: bool


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
    fromUser: FromUser | None = None
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
