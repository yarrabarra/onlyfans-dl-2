from typing import Any, List, Optional

from pydantic import BaseModel
from datetime import datetime


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


class Subscribe(BaseModel):
    id: int
    userId: int
    subscriberId: int
    date: datetime
    duration: int
    startDate: datetime
    expireDate: datetime
    cancelDate: Any
    price: int
    regularPrice: int
    discount: int
    earningId: int
    action: str
    type: str
    offerStart: Any
    offerEnd: Any
    isCurrent: bool


class SubscribedByData(BaseModel):
    price: int
    newPrice: int
    regularPrice: int
    subscribePrice: int
    discountPercent: int
    discountPeriod: int
    subscribeAt: datetime
    expiredAt: datetime
    renewedAt: datetime
    discountFinishedAt: Any
    discountStartedAt: Any
    status: Any
    isMuted: bool
    unsubscribeReason: str
    duration: str
    showPostsInFeed: bool
    subscribes: List[Subscribe]
    hasActivePaidSubscriptions: bool


class Profile(BaseModel):
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
    subscriptionBundles: List[SubscriptionBundle]
    isPaywallRequired: bool
    unprofitable: bool
    listsStates: List[ListsState]
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
    joinDate: datetime
    isReferrerAllowed: bool
    about: str
    rawAbout: str
    website: str
    wishlist: Any
    location: Any
    postsCount: int
    archivedPostsCount: int
    privateArchivedPostsCount: int
    photosCount: int
    videosCount: int
    audiosCount: int
    mediasCount: int
    lastSeen: datetime
    favoritesCount: int
    favoritedCount: int
    showPostsInFeed: bool
    canReceiveChatMessage: bool
    isPerformer: bool
    isRealPerformer: bool
    isSpotifyConnected: bool
    subscribersCount: Any
    hasPinnedPosts: bool
    hasLabels: bool
    canChat: bool
    callPrice: int
    isPrivateRestriction: bool
    showSubscribersCount: bool
    showMediaCount: bool
    subscribedByData: SubscribedByData
    subscribedOnData: Any
    canPromotion: bool
    canCreatePromotion: bool
    canCreateTrial: bool
    isAdultContent: bool
    canTrialSend: bool
    hadEnoughLastPhotos: bool
    hasLinks: bool
    finishedStreamsCount: int
    shouldShowFinishedStreams: bool
    hasSavedStreams: bool
    firstPublishedPostDate: datetime
    isSpringConnected: bool
    isFriend: bool
    isBlocked: bool
    canReport: bool
