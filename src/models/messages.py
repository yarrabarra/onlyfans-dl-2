from typing import Any
from datetime import datetime
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
    price: int
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
    subscribePrice: int
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
    currentSubscribePrice: int
    subscribedOn: Any
    subscribedOnExpiredNow: Any
    subscribedOnDuration: Any
    callPrice: int
    lastSeen: str
    canReport: bool


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
    fromUser: FromUser
    isFromQueue: bool
    canUnsendQueue: bool
    unsendSecondsQueue: int
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
