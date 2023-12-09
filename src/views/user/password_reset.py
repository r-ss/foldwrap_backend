from fastapi import status, BackgroundTasks

# from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from models.user import PasswordResetRequstBM, PasswordResetEmailBM
from services.users.password_reset import PasswordResetService

router = InferringRouter(tags=["User"])


@cbv(router)
class PasswordResetCBV:

    """CREATE"""

    @router.post("/user/password_forgot", status_code=status.HTTP_201_CREATED)
    async def password_forgot(self, background_tasks: BackgroundTasks, for_email: PasswordResetEmailBM):
        """Makes a password reset token and sending it to user's email"""
        result = await PasswordResetService.request_reset_token(background_tasks, for_email.for_email)
        return result

    @router.post("/user/password_reset", status_code=status.HTTP_200_OK)
    async def password_reset(self, reset_request: PasswordResetRequstBM):
        """Processing password reset token and decite to allow change user's password"""
        result = await PasswordResetService.use_reset_token(reset_request)
        return result
