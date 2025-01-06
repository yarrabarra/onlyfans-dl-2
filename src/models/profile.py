from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel


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
    id: int | str
    type: str
    name: str
    hasUser: bool
    canAddUser: bool


class Subscribe(BaseModel):
    action: str
    cancelDate: datetime | None = None
    date: datetime
    discount: int
    duration: int
    earningId: int
    expireDate: datetime | None = None
    id: int
    isCurrent: bool
    offerEnd: datetime | None = None
    offerStart: datetime | None = None
    price: Decimal
    regularPrice: Decimal
    startDate: datetime | None = None
    subscriberId: int
    type: str
    userId: int


class SubscribedByData(BaseModel):
    discountFinishedAt: datetime | None = None
    discountPercent: int
    discountPeriod: int
    discountStartedAt: datetime | None = None
    duration: str
    expiredAt: datetime
    hasActivePaidSubscriptions: bool
    newPrice: Decimal
    price: Decimal
    regularPrice: Decimal
    showPostsInFeed: bool | None = None
    status: str | None = None
    subscribeAt: datetime
    subscribePrice: Decimal
    subscribes: List[Subscribe]
    unsubscribeReason: str


class Profile(BaseModel):
    id: int

    avatar: str | None = None
    header: str | None = None
    username: str
    view: str
    name: str

    tipsMax: int
    tipsMin: int
    tipsMinInternal: int

    canAddSubscriber: bool
    canCommentStory: bool
    canEarn: bool
    canLookStory: bool
    canPayInternal: bool
    canRestrict: bool | None = None
    hasNotViewedStory: bool
    hasScheduledStream: bool
    hasStories: bool
    hasStream: bool
    isPaywallRequired: bool | None = None
    isRestricted: bool | None = None
    isVerified: bool
    subscribedIsExpiredNow: bool | None = None
    tipsEnabled: bool
    tipsTextEnabled: bool
    unprofitable: bool | None = None

    subscribedByExpireDate: datetime | None = None
    subscribePrice: Decimal

    listsStates: List[ListsState] = []
    subscriptionBundles: List[SubscriptionBundle] = []

    avatarThumbs: AvatarThumbs | None = None
    headerSize: HeaderSize | None = None
    headerThumbs: HeaderThumbs | None = None

    subscribedByData: SubscribedByData | None = None

    callPrice: Decimal | None = None
    currentSubscribePrice: Decimal | None = None

    firstPublishedPostDate: datetime | None = None
    joinDate: datetime | None = None
    renewedAt: datetime | None = None

    archivedPostsCount: int | None = None
    audiosCount: int | None = None
    finishedStreamsCount: int | None = None
    mediasCount: int | None = None
    photosCount: int | None = None
    postsCount: int | None = None
    privateArchivedPostsCount: int | None = None
    subscribersCount: int | None = None
    videosCount: int | None = None

    location: str | None = None
    subscribedOnData: SubscribedByData | None = None
    subscribedOnDuration: str | None = None
    subscribedOnExpiredNow: bool | None = None

    about: str | None = None
    lastSeen: str | None = None
    rawAbout: str | None = None
    website: str | None = None
    wishlist: str | None = None

    canChat: bool | None = None
    canCreatePromotion: bool | None = None
    canCreateTrial: bool | None = None
    canPromotion: bool | None = None
    canReceiveChatMessage: bool | None = None
    canReport: bool | None = None
    canTrialSend: bool | None = None
    hadEnoughLastPhotos: bool | None = None
    hasLabels: bool | None = None
    hasLinks: bool | None = None
    hasPinnedPosts: bool | None = None
    hasSavedStreams: bool | None = None
    hideChat: bool | None = None
    isAdultContent: bool | None = None
    isBlocked: bool | None = None
    isFriend: bool | None = None
    isMuted: bool | None = None
    isPerformer: bool | None = None
    isPrivateRestriction: bool | None = None
    isRealPerformer: bool | None = None
    isReferrerAllowed: bool | None = None
    isSpotifyConnected: bool | None = None
    isSpringConnected: bool | None = None
    shouldShowFinishedStreams: bool | None = None
    showMediaCount: bool | None = None
    showPostsInFeed: bool | None = None
    showSubscribersCount: bool | None = None
    subscribedBy: bool | None = None
    subscribedByAutoprolong: bool | None = None
    subscribedByExpire: bool | None = None
    subscribedOn: bool | None = None

    def __repr__(self):
        return f"{self.id} - {self.name}"
