import re
from datetime import datetime

# from typing import Dict

from bson import ObjectId
from pydantic import BaseModel, Field, constr

from dao.oid import OID
from models.meta import MetaBM


class FigmaLink(str):
    """Used to validate figma link
    example: https://www.figma.com/file/EgePe5Ftkvz9lgjsx211ko/Ikea---alegra-tu-sal%C3%B3n?...
    here is file key part               ^^^^^^^^^^^^^^^^^^^^^^  = 22 characters
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args):
        regex = re.compile("([a-zA-Z0-9]{22})")
        match = re.search(regex, v)
        if not match:
            raise ValueError("Link to figma seems invalid")
        return match.group()


class FigmaFileBM(BaseModel):
    """Represents figma file in database"""

    id: OID | None = Field(default_factory=ObjectId, alias="_id")
    owner: OID | None = None
    figma_file_key: constr(min_length=22, max_length=22)
    created: datetime | None = Field(default_factory=datetime.utcnow)
    json_downloaded: datetime | None = None
    comment: str | None = None  # internal comment must never be visible to any user
    meta: MetaBM | None = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat(), ObjectId: lambda oid: str(oid)}


class FigmaFileLinkBM(BaseModel):
    """Link to figma passed to initiate parsing etc."""

    link: FigmaLink
