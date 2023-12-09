import secrets

from datetime import datetime, timezone

from fastapi import HTTPException, status, BackgroundTasks

# from dao.dao_photo import PhotoDAOLayer
from dao.dao_user import UserDAOLayer
from dao.oid import OID
from log import log
from models.user import UserBM, UserProfileBM, UserRegBM, UserTokenBM, IPInfoBM
from models.email import EmailType, EmailBM
from services.misc.filesystem import FileSystemUtils
from services.users.auth import Auth

from services.email import EmailService

from dao.ress_redis import RessRedisAbstraction

from config import config

redis = RessRedisAbstraction()

UserDAO = UserDAOLayer()

fs = FileSystemUtils()


class UsersService:

    """CREATE SERVICE"""

    async def create(background_tasks: BackgroundTasks, user: UserRegBM, ip_info: IPInfoBM, nopassword=False) -> UserBM:
        """Create user in database and return it"""

        # def generate_6_digit_code():
        #     return str(random.randint(100000, 999999))

        if await UserDAO.is_email_registered(email=user.email):
            raise HTTPException(
                status_code=409,  # 409 - Conflict
                detail="User with this email already registered",
            )

        if not nopassword:
            user.userhash = Auth.hash_password(user.password.get_secret_value().casefold())
        new_user = UserBM(email=user.email.casefold(), userhash=user.userhash, created_ip=ip_info)

        new_user.registered_via = "web"
        if nopassword:
            new_user.registered_via = "google oauth"
            new_user.email_verified = True

        new_user_in_db = await UserDAO.create(new_user)
        new_user_in_db.userhash = "******"

        if not nopassword:
            # Web registration case

            # setting up email activation code into redis
            code = secrets.token_urlsafe(16)
            redis.set(f"activation-code:{ code }", new_user.email, exp=60 * 60 * 24 * 7)  # 7 days

            print("activation-code", code)

            email = EmailBM(
                type=EmailType.ConfirmEmail,
                recipient=new_user.email,
                template_model={"confirmation_code": code, "action_url": f"{config.HOST}/user/login?foldconfcode={code}"},
            )

            # await EmailService.send_email(email)
            # running in background
            background_tasks.add_task(EmailService.send_email, email)

        log("User registered", email=new_user_in_db.email, user_id=str(new_user_in_db.id), via=new_user.registered_via)

        return new_user_in_db

    """ CONFIRM EMAIL """

    async def confirm_email(code: str):
        """result = (success, message)"""
        r_email = redis.get(f"activation-code:{code}")

        if not r_email:
            return (False, "Code not found")

        db_user = await UserDAO.get_by_email(email=r_email)
        db_user.email_verified = True
        _ = await UserDAO.update(db_user)

        redis.delete(f"activation-code:{code}")

        log("User email confirmed", email=db_user.email)

        return (True, "Email confirmed")

    """ READ SERVICE """

    async def read_all() -> list[UserBM]:
        """Get all users from database and return them as a list"""
        return await UserDAO.read_all()

    # async def read_specific(id: OID) -> UserBM:
    #     """Get specific user from database and return"""
    #     return await UserDAO.read(id=id)

    async def read_specific(id: OID) -> UserBM:
        """Get specific user by id and return"""
        return await UserDAO.read(id)

    # """ UPDATE SERVICE """

    # async def edit_user(target_id: OID, input_user: UserRegBM, token: UserTokenBM) -> UserBM:
    #     """Change username of specific user in database and returu User with updated data"""

    #     user = await UserDAO.read(id=target_id)

    #     if str(user.id) != str(token.id):
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")

    #     if input_user.email:
    #         user.email = input_user.email
    #         updated = await UserDAO.update(user)
    #         return updated

    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seems like username not present")

    """ FILL PROFILE """

    async def fill_profile(profile: UserProfileBM, token: UserTokenBM) -> UserBM:
        user = await UserDAO.read(id=token.id)
        user.profile = profile
        user.last_activity = datetime.now(timezone.utc)
        updated_user = await UserDAO.update(user)
        # log(f'Profile for user "{ updated_user.username }" has been updated')
        return updated_user

    """ DELETE SERVICE """

    async def delete(id: OID, token: UserTokenBM):
        """Delete user from database"""

        user = await UserDAO.read(id)

        if str(user.id) != str(token.id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")

        # Delete all user photos from db
        # _ = await PhotoDAO.collection.delete_many({"owner": user.id})

        # Delete all user photos from disk
        # fs.remove_directory(user.media_dir)

        result = await UserDAO.delete(id=user.id)
        # log(f'User "{ user.username }" has been deleted', level="warning")

        log("User deleted", level="info", email=user.email, user_id=str(user.id))
        return result
