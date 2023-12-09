from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class SubscriptionDetailsBM(BaseModel):
    subscription_id: int | None = None
    created_at: datetime
    updated_at: datetime
    customer_portal_url: str | None = None

    store_id: int
    customer_id: int
    order_id: int
    order_item_id: int
    product_id: int
    variant_id: int
    product_name: str
    variant_name: str
    user_name: str
    user_email: str
    status: str
    status_formatted: str
    card_brand: Optional[str] = None
    card_last_four: Optional[str] = None
    pause: Optional[bool] = None
    cancelled: bool
    trial_ends_at: datetime

    renews_at: datetime
    ends_at: Optional[datetime] = None
    test_mode: bool | None = None
