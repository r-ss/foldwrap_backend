# from bson import ObjectId
from datetime import datetime

from fastapi import HTTPException

from dao.dao import BasicDAOLayer
from models.user import UserBM


class UserDAOLayer(BasicDAOLayer):
    def __init__(self):
        super().__init__()
        self.collection_name = "user"
        self.model = UserBM
        self.collection = self.db[self.collection_name]

    async def read(self, id: str, removehash=True):
        """Overriding superclass function
        With added functionality to remove user hash from output
        """
        user = await super().read(id=id)
        if removehash:
            user.userhash = "read - censored in dao"
        return user

        # if (db_entry := await self.collection.find_one({"_id": ObjectId(id)})) is not None:
        #     if removehash:
        #         if "userhash" in db_entry:
        #             db_entry["userhash"] = "read - censored in dao"

        #     return self.model.parse_obj(db_entry)
        # raise HTTPException(status_code=404, detail=f"User {id} not found")

    async def update_last_activity(self, user: UserBM) -> None:
        db_user = await super().read(id=user.id)
        db_user.last_activity = datetime.utcnow()
        _ = await super().update(db_user)

    # async def is_user_registered(self, email: str) -> bool:
    #     """To check if user with email already registered or no"""
    #     if (_ := await self.collection.find_one({"email": email.casefold()})) is not None:
    #         return True
    #     return False
    async def read_all(self, limit=1000):
        """Read all users and return as a list of Pydantic objects"""
        bin = []
        for row in await self.collection.find().to_list(limit):
            bin.append(self.model.parse_obj(row))

        for item in bin:
            item.userhash = "******"

        return bin

    async def is_email_registered(self, email: str) -> bool:
        """To check if user with email already registered or no"""
        if (_ := await self.collection.find_one({"email": email.casefold()})) is not None:
            return True
        return False

    # async def get_by_username(self, username: str, removehash=True):
    #     if (db_entry := await self.collection.find_one({"username": username.casefold()})) is not None:
    #         if removehash:
    #             if "userhash" in db_entry:
    #                 db_entry["userhash"] = "******"

    #         return self.model.parse_obj(db_entry)
    #     raise HTTPException(status_code=404, detail=f"User with username {username} not found")

    async def get_by_email(self, email: str, removehash=True):
        if (db_entry := await self.collection.find_one({"email": email.casefold()})) is not None:
            if removehash:
                if "userhash" in db_entry:
                    db_entry["userhash"] = "******"

            return self.model.parse_obj(db_entry)
        raise HTTPException(status_code=404, detail=f"User with email {email} not found")

    async def update(self, item, removehash=True):
        updated_user = await super().update(item, removehash=removehash)
        if removehash:
            updated_user.userhash = "******"
        return updated_user
