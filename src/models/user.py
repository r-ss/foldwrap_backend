from datetime import datetime
from enum import Enum

from bson import ObjectId
from fastapi import Form
from pydantic import BaseModel, EmailStr, Field, SecretStr, constr

from dao.oid import OID
from models.meta import MetaBM

from models.lemonsqueezy.subscription_details import SubscriptionDetailsBM


class ProReason(str, Enum):
    ON_TRIAL = "on_trial"
    PAID = "paid"
    DEMO = "demo"  # when user is on demo period
    TEST = "test"  # for testing purposes


class PaidStatus(str, Enum):
    ON_TRIAL = "on_trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    LEMONSQUEEZY = "lemonsqueezy"


class IPInfoBM(BaseModel):
    """Ip info about user's reg and login
    https://ipinfo.io
    """

    x_real_ip: str  # << passed from nginx, saved as str because FUCK YOU PYDANTIC (mongo_json_encoder error)
    x_forwarded_for: str  # << passed from nginx, saved as str because FUCK YOU PYDANTIC (mongo_json_encoder error)

    """
    TODO: following fields are returned by ipinfo.io
    hostname: str | None = None # "239.pool92-59-207.dynamic.orange.es"
    city: str | None = None # "Madrid"
    region: str | None = None # "Madrid"
    country: str | None = None # "ES"
    loc: str | None = None # locatoc coords "40.4165,-3.7026"
    """


class UserProfileBM(BaseModel):
    name: constr(min_length=2, max_length=64)
    about: constr(max_length=512) | None


class UserBM(BaseModel):

    """Represents registered user
    Currently we allowing login by email only

    Instead of saving user's password we save hash like this:
    "$4b$32$AzjaznqlSFwiQSctaP3Rc.hrusgal2977/.Ny7.CtJ9ELbiHUAMGi"
    and checking it with bcrypt.checkpw upon login attemp

    last_login field is updating in services.users.auth every time user login

    """

    id: OID | None = Field(default_factory=ObjectId, alias="_id")
    email: EmailStr
    email_verified: bool = False
    is_superadmin: bool | None = False
    userhash: str | None = None

    created: datetime | None = Field(default_factory=datetime.utcnow)
    created_ip: IPInfoBM | None = None
    last_login: datetime | None = Field(default_factory=datetime.utcnow)
    last_login_ip: IPInfoBM | None = None

    last_activity: datetime | None = None  # TODO - write to this field
    comment: str | None = None  # internal comment must never be visible to any user
    registered_via: str | None = None
    profile: UserProfileBM | None = None
    meta: MetaBM | None = None

    pro_customer: bool = False
    pro_reason: ProReason | None = None  # paid / demo

    paid_status: PaidStatus | None = None  # on_trial / active / expired / cancelled
    paid_via: PaymentMethod | None = None  # lemonsqueezy / stripe / whatever
    subscription_details: SubscriptionDetailsBM | None = None
    demo_expires: datetime | None = None

    # @property
    # def media_dir(self) -> str:
    #     return Path(config.DATA_DIR).joinpath( slugify(self.username) )

    class Config:
        # populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat(), ObjectId: lambda oid: str(oid)}


class UserRenderBM(UserBM):
    """Used for FastAPI JSON output replacing Mongo's _id to id and userhash to dummy ******"""

    id: OID | None = None
    # userpic: str | dict | None

    def __init__(self, **pydict):
        super().__init__(**pydict)
        self.id = pydict.pop("_id")
        self.userhash = "******"
        self.comment = "****"
        # self.userpic = self.userpic_hash_to_url()


class UserRegBM(BaseModel):  # used upon user registeration
    email: EmailStr
    password: SecretStr | None = None
    userhash: str | None = None


class UserTokenBM(BaseModel):  # used in token_required
    email: EmailStr
    id: str
    is_superadmin: bool
    iat: datetime  # constr(max_length=100)
    exp: datetime  # constr(max_length=100)
    scope: constr(max_length=15)


class UserRefreshTokenBM(BaseModel):  # used in refresh_token procedure
    refresh_token: str


class UserLoginFormBM(BaseModel):  # used upon login
    username: EmailStr = Form(...)
    password: str = Form(...)
    client: dict | None = Form(...)


class PasswordResetEmailBM(BaseModel):
    for_email: EmailStr


class PasswordResetRequstBM(BaseModel):
    email: EmailStr
    code: str
    new_password: SecretStr


class PasswordResetTokenBM(BaseModel):

    """Represents token for password reset procedure
    Basic workflow described here: https://supertokens.com/blog/implementing-a-forgot-password-flow

    """

    user_id: OID
    user_email: EmailStr
    token_hash: str

    class Config:
        json_encoders = {ObjectId: lambda oid: str(oid)}
