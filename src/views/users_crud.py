from fastapi import Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from config import config
from dao.oid import OID
from models.user import UserProfileBM, UserRegBM, UserRenderBM, UserTokenBM, IPInfoBM
from services.misc.utils import send_message
from services.users.auth import Auth, token_required
from services.users.crud import UsersService


router = InferringRouter(tags=["User"])


@cbv(router)
class UsersCBV:

    """CREATE"""

    @router.post("/users", status_code=status.HTTP_201_CREATED)
    async def create_user(
        self, background_tasks: BackgroundTasks, request: Request, user: UserRegBM
    ) -> UserRenderBM:  # FastAPI routes don't need `response_model=` anymore in favor of adding the return type to your function signature such as `async def create_thing() -> Thing:`
        if not user.password or not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password must be provided for registration",
            )

        if not Auth.is_password_valid(user.password.get_secret_value().lower()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=config.AUTH_PASSWORD_REGEX["failmessage"],
            )

        ip_info = None
        if request.headers.get("X-Real-IP") and request.headers.get("X-Forwarded-For"):
            ip_info = IPInfoBM(x_real_ip=request.headers.get("X-Real-IP"), x_forwarded_for=request.headers.get("X-Forwarded-For"))

        db_user = await UsersService.create(background_tasks, user, ip_info)

        send_message(f"User {db_user.email} registered")

        return db_user

    """ CONFIRM EMAIL """

    @router.get("/confirm", status_code=status.HTTP_200_OK, summary="Confirm email by a 6-digit code")
    async def confirm_email(self, code: str):
        # if not re.fullmatch(r'[A-Za-a0-9]{16}', code):
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Code not meet requirements",
        #     )

        (result, message) = await UsersService.confirm_email(code)

        return JSONResponse(status_code=status.HTTP_200_OK if result else status.HTTP_400_BAD_REQUEST, content={"result": result, "message": message})

    """ READ """

    @router.get("/users", status_code=status.HTTP_200_OK, summary="Read all users")
    async def read_all(self) -> list[UserRenderBM]:
        return await UsersService.read_all()

    @router.get("/user/{id}", status_code=status.HTTP_200_OK, summary="Read specific user by id")
    async def read_specific(self, id: OID) -> UserRenderBM:
        return await UsersService.read_specific(id)

    """ PATCH """

    # @router.patch("/users/{id}", status_code=status.HTTP_200_OK, response_model=UserRenderBM)
    # async def update_user(self, id: OID, user: UserRegBM, token: UserTokenBM = Depends(token_required)):
    #     return await UsersService.edit_user(id, user, token)

    """ FILL PROFILE """

    @router.patch("/user/profile", status_code=status.HTTP_200_OK, summary="Fill user profile")
    async def update_user_profile(self, profile: UserProfileBM, token: UserTokenBM = Depends(token_required)) -> UserRenderBM:
        return await UsersService.fill_profile(profile, token)

    """ DELETE """

    @router.delete("/user/{id}")
    async def delete_user(self, id: OID, token: UserTokenBM = Depends(token_required)):
        await UsersService.delete(id, token)

        send_message(f"User {id} deleted")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"result": f"user {id} deleted"})
