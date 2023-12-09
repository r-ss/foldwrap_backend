from datetime import datetime
from re import compile

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from config import config
from dao.dao_user import UserDAOLayer
from dao.oid import OID
from models.user import UserBM, UserTokenBM, IPInfoBM

UserDAO = UserDAOLayer()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def token_required(token: str = Depends(oauth2_scheme)) -> UserTokenBM:
    """Decode user token from header. Used in views that requires authentication
    Example in FastAPI Docs:
    https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
    """
    try:
        dict = jwt.decode(token, config.SECRET_KEY, algorithms=[config.AUTH_HASHING_ALGORITHM])
        prstoken = UserTokenBM.parse_obj(dict)
        return prstoken
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error decoding token (Signature Expired)",
        )
    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error decoding token (Signature Invalid)",
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error decoding token (Decode Error)",
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error decoding token (Other Error)",
        )


def check_ownership(id: OID, token: UserTokenBM) -> None:
    """
    Compare id of object's owner with id of current user
    Throw an HTTPException if current user is not own object
    Method can be invoked in a middle of views to stop unauthorized operations
    """
    if not token.is_superadmin and not str(id) == str(token.id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seems like you are not authorized to this",
        )


def sudo_only(token: UserTokenBM) -> None:
    """
    Throw an HTTPException if current user is not superuser
    Method can be invoked in a middle of views to stop unauthorized operations
    """
    if not token.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Seems like you are not authorized to this (sudo_only)",
        )


class Auth:
    # def is_username_valid(username) -> bool:
    #     """Username validation"""
    #     regex = compile(config.AUTH_USERNAME_REGEX["regex"])
    #     return regex.match(username.casefold()) is not None

    def is_password_valid(password) -> bool:
        """Password validation"""
        regex = compile(config.AUTH_PASSWORD_REGEX["regex"])
        return regex.match(password.casefold()) is not None

    def hash_password(pwd) -> str:
        """Application-wide method to get hash from a password
        Used upon registration and login
        """
        pwd = pwd.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd, salt).decode("utf-8")

    def encode_access_token(user: UserBM):
        payload = {
            "exp": datetime.utcnow() + config.AUTH_ACCESS_TOKEN_EXPIRATION_TIME,  # set access token time limit
            "iat": datetime.utcnow(),  # issued at
            "scope": "access_token",
            "email": user.email,
            "id": str(user.id),
            "is_superadmin": user.is_superadmin,
        }
        return jwt.encode(payload, config.SECRET_KEY, algorithm=config.AUTH_HASHING_ALGORITHM)  # encrypt payload into token

    def encode_refresh_token(user: UserBM):
        payload = {
            "exp": datetime.utcnow() + config.AUTH_REFRESH_TOKEN_EXPIRATION_TIME,  # set refresh token time limit
            "iat": datetime.utcnow(),  # issued at
            "scope": "refresh_token",
            "email": user.email,
            "id": str(user.id),
            "is_superadmin": user.is_superadmin,
        }
        return jwt.encode(payload, config.SECRET_KEY, algorithm=config.AUTH_HASHING_ALGORITHM)  # encrypt payload into token

    async def check_refresh_token(refresh_token):
        try:
            dict = jwt.decode(refresh_token, config.SECRET_KEY, algorithms=[config.AUTH_HASHING_ALGORITHM])
            if dict["scope"] == "refresh_token":
                user = await UserDAO.read(id=dict["id"])
                new_access_token = Auth.encode_access_token(user)
                new_refresh_token = Auth.encode_refresh_token(user)
                return new_access_token, new_refresh_token

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    async def login(email: str, password: str, ip_info: IPInfoBM) -> bool:
        email = email.casefold()
        password = password.casefold()

        user_with_hash = await UserDAO.get_by_email(email=email, removehash=False)

        if user_with_hash.userhash is None and user_with_hash.registered_via == "web":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not have a password in record, please contact support")

        if user_with_hash.userhash is None and user_with_hash.registered_via == "google oauth":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User registered via Google OAuth. Please use Google OAuth login instead")

        # If password correct login and return token to client
        if bcrypt.checkpw(password.encode("utf-8"), user_with_hash.userhash.encode("utf-8")):
            access_token = Auth.encode_access_token(user_with_hash)
            refresh_token = Auth.encode_refresh_token(user_with_hash)

            user_with_hash.last_login = datetime.utcnow()
            user_with_hash.last_login_ip = ip_info
            logged_in_user = await UserDAO.update(user_with_hash)

            return logged_in_user, access_token, refresh_token
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong password")

    async def issue_tokens_after_oauth_login(email: str) -> bool:
        email = email.casefold()

        db_user = await UserDAO.get_by_email(email=email)

        access_token = Auth.encode_access_token(db_user)
        refresh_token = Auth.encode_refresh_token(db_user)

        db_user.last_login = datetime.utcnow()

        logged_in_user = await UserDAO.update(db_user)

        return logged_in_user, access_token, refresh_token
