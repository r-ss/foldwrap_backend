from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, Field

from dao.oid import OID

# from models.user import UserRenderBM


class BMTest(BaseModel):
    """Used only in auto-tests"""

    id: OID | None = Field(default_factory=ObjectId, alias="_id")
    content: str
    # created: datetime | None = Field(default_factory=datetime.utcnow)
    # child: Union[OID, UserRenderBM] | None

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid),
        }
