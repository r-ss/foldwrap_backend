from datetime import datetime
import json
from urllib.parse import urlencode

import httpx
from fastapi import Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from config import config
from dao.dao_user import UserDAOLayer
from log import log
from models.user import UserRefreshTokenBM, UserRegBM, UserTokenBM, IPInfoBM
from services.misc.utils import send_message
from services.users.auth import Auth, token_required
from services.users.crud import UsersService

UserDAO = UserDAOLayer()


router = InferringRouter(tags=["Authentication"])


@cbv(router)
class AuthCBV:

    """GOOGLE LOGIN"""

    @router.get("/get-google-oauth-link", status_code=status.HTTP_202_ACCEPTED, summary="Generate link address for login users with Google OAuth2")
    async def get_google_oauth_link(self):
        # Perform Google OAuth2 authentication
        google_auth_url = "https://accounts.google.com/o/oauth2/auth"

        # Redirect the user to Google's OAuth2 consent screen
        auth_params = {
            "client_id": config.GOOGLE_OAUTH_CLIENT_ID,
            "redirect_uri": "https://foldwrap.com/user/login",
            "scope": "openid profile email",  # Adjust scopes as needed
            "response_type": "code",
        }

        google_auth_url_with_params = f"{google_auth_url}?{urlencode(auth_params)}"
        return JSONResponse({"url_request_success": True, "url": google_auth_url_with_params})

    @router.get("/google-callback", summary="Processing callback from Google OAuth2 and decide to login or register user")
    async def google_callback(self, background_tasks: BackgroundTasks, request: Request, code: str, error: str = None, error_description: str = None):
        if error:
            raise HTTPException(status_code=400, detail=f"Google OAuth2 Error: {error_description}")

        # Exchange the authorization code for tokens
        token_url = "https://accounts.google.com/o/oauth2/token"

        token_params = {
            "code": code,
            "client_id": config.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": config.GOOGLE_OAUTH_SECRET,
            "redirect_uri": "https://foldwrap.com/user/login",
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=token_params)

        if response.status_code != 200:
            log("Google OAuth token request failed", response_text=response.text, level="error")
            raise HTTPException(status_code=400, detail=f"Token request failed: {response.text}")

        token_data = response.json()

        access_token = token_data["access_token"]

        # Make a request to Google's userinfo endpoint to get his email
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)

        if response.status_code != 200:
            log("Google OAuth userinfo request failed", level="error", message=response.text)
            raise HTTPException(status_code=400, detail=f"Userinfo request failed: {response.text}")

        userinfo_data = response.json()
        user_email = userinfo_data["email"]  # Now, you have the user's email

        registering_user = UserRegBM(email=user_email)

        ip_info = None
        if request.headers.get("X-Real-IP") and request.headers.get("X-Forwarded-For"):
            ip_info = IPInfoBM(x_real_ip=request.headers.get("X-Real-IP"), x_forwarded_for=request.headers.get("X-Forwarded-For"))

        if await UserDAO.is_email_registered(email=user_email):
            log("User logged-in via google oauth", level="debug", email=user_email)

            db_user = await UserDAO.get_by_email(email=user_email)

            db_user.last_login = datetime.utcnow()
            db_user.last_login_ip = ip_info
            _ = await UserDAO.update(db_user)

            send_message(f"User {user_email} logged in via google oauth")
        else:
            db_user = await UsersService.create(background_tasks, registering_user, ip_info, nopassword=True)
            send_message(f"User {db_user.email} registered via google oauth")

        # Issue own tokens and send to frontend
        user, access_token, refresh_token = await Auth.issue_tokens_after_oauth_login(user_email)
        user.userhash = "******"  # replacing hash to ensure it's not going to response
        user.comment = "****"

        return JSONResponse(
            {
                "auth": True,
                "auth_via": "google oauth",
                "user": json.loads(user.json()),
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        )

    """ LOGIN """

    @router.post(
        "/token",
        status_code=status.HTTP_202_ACCEPTED,
        summary="Login user and get access/refresh tokens",
    )
    async def login(self, request: Request, form_data: OAuth2PasswordRequestForm = Depends()):

        def bad_req(msg: str):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        if not form_data.username or not form_data.password:
            bad_req("Email and password must be provided for login")

        if not Auth.is_password_valid(form_data.password):
            bad_req(config.AUTH_PASSWORD_REGEX["failmessage"])

        ip_info = None
        if request.headers.get("X-Real-IP") and request.headers.get("X-Forwarded-For"):
            ip_info = IPInfoBM(x_real_ip=request.headers.get("X-Real-IP"), x_forwarded_for=request.headers.get("X-Forwarded-For"))

        user, access_token, refresh_token = await Auth.login(form_data.username, form_data.password, ip_info)
        user.userhash = "******"
        user.comment = "****"

        log("User logged-in", level="debug", email=user.email)

        return {
            "auth": True,
            "user": json.loads(user.json()),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    """ REFRESH TOKEN """

    @router.patch("/token", status_code=status.HTTP_202_ACCEPTED, summary="Refresh token")
    async def refresh_token(self, ref_token: UserRefreshTokenBM):
        new_access_token, new_refresh_token = await Auth.check_refresh_token(ref_token.refresh_token)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }

    """ SECRET PAGE, USED IN TESTS TO ENSURE TOKEN MECHANIC WORKING """

    @router.get("/secretpage", status_code=status.HTTP_200_OK, summary="Works only within tests")
    def secretpage(self, token: UserTokenBM = Depends(token_required)):
        return {"message": "this is secret message"}
