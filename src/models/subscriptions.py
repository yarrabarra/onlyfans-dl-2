from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel


class Subscribe(BaseModel):
    id: int
    userId: int
    subscriberId: int
    date: str
    duration: int
    startDate: datetime
    expireDate: datetime
    cancelDate: datetime | None
    price: Decimal
    regularPrice: Decimal
    discount: int
    earningId: int
    action: str
    type: str
    offerStart: Any
    offerEnd: Any
    isCurrent: bool


class SubscribedByData(BaseModel):
    price: Decimal
    newPrice: Decimal
    regularPrice: Decimal
    subscribePrice: Decimal
    discountPercent: int
    discountPeriod: int
    subscribeAt: datetime
    expiredAt: datetime
    renewedAt: Optional[datetime]
    discountFinishedAt: datetime | None
    discountStartedAt: datetime | None
    status: Any
    isMuted: Optional[bool] = False
    unsubscribeReason: str
    duration: str
    showPostsInFeed: bool | None = None
    subscribes: List[Subscribe]
    hasActivePaidSubscriptions: bool
