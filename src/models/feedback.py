from enum import Enum
from datetime import datetime
from pydantic import BaseModel, constr, Field, EmailStr
from bson import ObjectId
from dao.oid import OID


class FeedbackTheme(str, Enum):
    TEST = "test"
    GENERAL = "general"
    CUSTOMPLAN = "customplan"


class FeedbackEntryBM(BaseModel):

    """Represents a feedback sent though form on /contact
    when this message is sended, we need to set the "resolved" field to True
    """

    id: OID | None = Field(default_factory=ObjectId, alias="_id")
    theme: FeedbackTheme
    email: EmailStr
    name: constr(max_length=64) | None = None
    message: constr(min_length=2, max_length=2048)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)

    comment: constr(max_length=256) | None = None
    resolved: bool | None = False  # means sended something to provided email or not
    resolved_at: datetime | None = None

    class Config:
        json_encoders = {datetime: lambda dt: dt.isoformat(), ObjectId: lambda oid: str(oid)}


class FeedbackEntryEditBM(BaseModel):
    theme: FeedbackTheme
    email: EmailStr
    name: constr(max_length=64) | None = None
    message: constr(min_length=2, max_length=2048)
