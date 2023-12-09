from enum import StrEnum
from pydantic import BaseModel, EmailStr


class EmailType(StrEnum):
    # to be used as a Postmark template name
    ConfirmEmail = "confirm-email"
    PasswordReset = "password-reset"


class EmailBM(BaseModel):

    """Represents email to be sent to users"""

    type: EmailType
    sender: str | None = '"Foldwrap" <robot@foldwrap.com>'
    recipient: EmailStr
    # subject: str | None = None
    template_model: dict | None = None
