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
    price: int
    canBuy: bool


class Author(BaseModel):
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
    isMuted: bool
    isRestricted: bool
    canRestrict: bool
    subscribedBy: bool
    subscribedByExpire: bool
    subscribedByExpireDate: datetime
    subscribedByAutoprolong: bool
    subscribedIsExpiredNow: bool
    currentSubscribePrice: int
    subscribedOn: bool
    subscribedOnExpiredNow: Any
    subscribedOnDuration: Any
    showPostsInFeed: bool
    canTrialSend: bool


class Option(BaseModel):
    id: int
    name: str
    count: int
    isVoted: bool


class Voting(BaseModel):
    finishedAt: str
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
