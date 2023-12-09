import secrets
import urllib.parse

import bcrypt
from fastapi import HTTPException, BackgroundTasks

from config import config

# from dao.dao_passwordresettoken import PasswordResetTokenDAOLayer
from dao.dao_user import UserDAOLayer
from log import log

from pydantic import EmailStr
from models.user import PasswordResetRequstBM
from models.email import EmailType, EmailBM
from services.users.auth import Auth

from services.email import EmailService

from dao.ress_redis import RessRedisAbstraction


UserDAO = UserDAOLayer()
redis = RessRedisAbstraction()


class PasswordResetService:

    """CREATE SERVICE"""

    async def request_reset_token(background_tasks: BackgroundTasks, for_email: EmailStr):
        """Here we making a password reset token and sending it to user's email"""

        # def create_reset_token(data: dict):
        #     to_encode = data.copy()
        #     expire = datetime.utcnow() + timedelta(minutes=30)
        #     to_encode.update({"exp": expire})
        #     encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm="HS256")
        #     return encoded_jwt

        email = for_email.casefold()

        if not await UserDAO.is_email_registered(email):
            raise HTTPException(
                status_code=400,  # 400 - Bad request
                detail="User with this email is not registered",
            )

        user = await UserDAO.get_by_email(email)

        code = secrets.token_urlsafe(16)
        email_hashed = Auth.hash_password(user.email)

        print("code", code)
        print("email_hashed", email_hashed)

        redis.set(f"password-reset-code:{code}", email_hashed, exp=60 * 60)  # 1 hour

        log("Sending email with token")

        urlencoded_email = urllib.parse.quote_plus(user.email)

        email = EmailBM(
            type=EmailType.PasswordReset,
            recipient=user.email,
            template_model={"confirmation_code": code, "action_url": f"{config.HOST}/password_reset?code={code}&email={urlencoded_email}"},
        )

        # email_sending_result = await EmailService.send_email(email)
        # running in background
        background_tasks.add_task(EmailService.send_email, email)

        return {"result": True}

    async def use_reset_token(reset_request: PasswordResetRequstBM):
        """Here we check and use password reset token to change user's password"""

        email_hash = redis.get(f"password-reset-code:{reset_request.code}")
        if not email_hash:
            raise HTTPException(
                status_code=401,
                detail="Provided reset code is invalid",
            )

        if not await UserDAO.is_email_registered(email=reset_request.email):
            raise HTTPException(
                status_code=400,  # 400 - Bad request
                detail="User with this email is not registered",
            )

        user = await UserDAO.get_by_email(email=reset_request.email, removehash=False)

        # print(reset_request.reset_token.encode("utf-8"))
        # print(token_hash.encode("utf-8"))

        if not bcrypt.checkpw(reset_request.email.encode("utf-8"), email_hash.encode("utf-8")):
            raise HTTPException(
                status_code=401,
                detail="Provided reset token is invalid",
            )

        new_password_hash = Auth.hash_password(reset_request.new_password.get_secret_value().casefold())

        user.userhash = new_password_hash

        print("user.userhash", user.userhash)
        new_userss = await UserDAO.update(user, removehash=False)
        print("new_userss.userhash", new_userss.userhash)

        # token.used = True
        # token.used_at = datetime.utcnow()

        redis.delete(f"password-reset-code:{reset_request.code}")

        log("User password reset completed", email=user.email)

        return {"result": True}
