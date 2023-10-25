from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

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


class Author(BaseModel):
    avatar: str
    avatarThumbs: AvatarThumbs
    canAddSubscriber: bool
    canCommentStory: bool
    canEarn: bool
    canLookStory: bool
    canPayInternal: bool
    canRestrict: bool
    canTrialSend: bool
    currentSubscribePrice: Decimal
    hasNotViewedStory: bool
    hasScheduledStream: bool
    hasStories: bool
    hasStream: bool
    header: str
    headerSize: HeaderSize
    headerThumbs: HeaderThumbs
    id: int
    isMuted: Optional[bool] = False
    isPaywallRequired: bool
    isRestricted: bool
    isVerified: bool
    name: str
    showPostsInFeed: bool
    subscribedBy: bool
    subscribedByAutoprolong: bool
    subscribedByExpire: bool
    subscribedByExpireDate: datetime
    subscribedIsExpiredNow: bool
    subscribedOn: bool
    subscribedOnDuration: Any
    subscribedOnExpiredNow: Any
    subscribePrice: Decimal
    subscriptionBundles: list[SubscriptionBundle]
    tipsEnabled: bool
    tipsMax: int
    tipsMin: int
    tipsMinInternal: int
    tipsTextEnabled: bool
    unprofitable: bool
    username: str
    view: str


class Option(BaseModel):
    id: int
    name: str
    count: Optional[int]
    isVoted: bool


class Voting(BaseModel):
    finishedAt: Optional[str]
    options: list[Option]
    total: int


class Post(BaseModel):
    responseType: str
    id: int
    postedAt: Optional[datetime] = None
    postedAtPrecise: str
    expiredAt: Any
    author: Author
    text: str
    rawText: str
    lockedText: bool
    isFavorite: bool
    canReport: bool
    canDelete: bool
    canComment: bool
    canEdit: bool
    isPinned: bool
    favoritesCount: int
    mediaCount: int
    isMediaReady: bool
    voting: Voting | list
    isOpened: bool
    canToggleFavorite: bool
    streamId: Any
    price: Any
    hasVoting: bool
    isAddedToBookmarks: bool
    isArchived: bool
    isPrivateArchived: bool
    isDeleted: bool
    hasUrl: bool
    isCouplePeopleMedia: bool
    commentsCount: int
    mentionedUsers: list
    linkedUsers: list
    linkedPosts: list
    tipsAmount: str
    tipsAmountRaw: Decimal
    media: list[MediaItem]
    canViewMedia: bool
    preview: list

    def get_postdate(self):
        if self.postedAt is None:
            return "1970-01-01"  # Epoch failsafe if date is not present
        return self.postedAt.strftime("%Y-%m-%d")

    def is_viewable(self):
        return self.canViewMedia
