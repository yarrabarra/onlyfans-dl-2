from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from .media import MediaItem
from .profile import Profile


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
    expiredAt: datetime | None = None
    author: Profile
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
    streamId: str | None = None
    price: Decimal | None = None
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

    def get_date(self):
        if self.postedAt is None:
            return "1970-01-01"  # Epoch failsafe if date is not present
        return self.postedAt.strftime("%Y-%m-%d")

    def is_viewable(self):
        return self.canViewMedia

    def get_profile_id(self):
        return self.author.id
