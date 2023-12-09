import json
import pathlib
from datetime import datetime

import httpx
from fastapi import HTTPException, status

from config import config

# from dao.dao_figma_file import FigmaFileDAOLayer
from dao.dao_user import UserDAOLayer
from log import log
from models.figma_file import FigmaFileBM, FigmaFileLinkBM
from services.misc.filesystem import FileSystemUtils as fs

UserDAO = UserDAOLayer()
# FigmaFileDAO = FigmaFileDAOLayer()


async def make_convert_request(figma_file_key: str):
    host = "127.0.0.1"
    if config.PRODUCTION:
        host = "service-figma-to-dom"

    url = f"http://{host}:3001/convert/{figma_file_key}"
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=20.0)
        except httpx.ConnectError:
            log("Internal connection error", lever="error", figma_file=figma_file_key)
            raise HTTPException(
                status_code=500,
                detail="Internal service-figma-to-dom connection error",
            )
        except httpx.ReadTimeout:
            log("Internal connection timeout", lever="error", figma_file=figma_file_key)
            raise HTTPException(
                status_code=500,
                detail="Internal service-figma-to-dom read timeout",
            )
        return resp.json()


class FigmaService:
    async def get_status():
        host = "127.0.0.1"
        if config.PRODUCTION:
            host = "service-figma-to-dom"

        url = f"http://{host}:3001/status"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, timeout=5.0)
            except httpx.ConnectError:
                log("Internal connection error while probe /status for dom service", lever="error")
                # err =  HTTPException(
                #     status_code=500,
                #     detail="Internal service-figma-to-dom connection error",
                # )
                return {"resource": "figma_to_dom_service_status", "result": "Internal connection error while probe /status for dom service", "service_response": None}
            except httpx.ReadTimeout:
                log("Internal connection timeout error while probe /status for dom service", lever="error")
                # raise HTTPException(
                #     status_code=500,
                #     detail="Internal service-figma-to-dom read timeout",
                # )
                return {"resource": "figma_to_dom_service_status", "result": "Internal connection timeout error while probe /status for dom service", "service_response": None}

        return {"resource": "figma_to_dom_service_status", "result": "service ok", "service_response": resp.json()}

        # if response["resource"] == "figma_to_dom_service":
        #     result = "service ok"
        # else:
        #     result = "service error"
        # return {"resource": "figma_to_dom_service_status", "result": result, "service_response": response}

    async def process_figma_link(figma_link: FigmaFileLinkBM) -> FigmaFileBM:
        key = figma_link.link
        dir = pathlib.Path(config.DATA_DIR_FIGMA_FILES).joinpath(key)

        figma_file_object = FigmaFileBM(figma_file_key=key)

        json_file_path = dir.joinpath("file.json")
        # json_images_path = dir.joinpath('images.json')

        if fs.is_file_exist(json_file_path):
            fs.remove_directory(dir)
            # return {
            #     "message": "json was already downloaded",
            #     "mod_time": datetime.utcfromtimestamp( json_file_path.stat().st_mtime ),
            #     "figma_file": figma_file_object
            # }

        # async def download_json():
        headers = {"X-FIGMA-TOKEN": config.FIGMA_API_TOKEN}
        url = f"https://api.figma.com/v1/files/{figma_link.link}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        # Ensure the request was successful
        if response.status_code == 200:
            data = response.json()

            # Write the data to a file
            fs.check_dir(dir)
            with open(json_file_path, "w") as f:
                json.dump(data, f, indent=4)

            figma_file_object.json_downloaded = datetime.utcnow()

        else:
            log("Request to process figma link failed", lever="error", figma_file=key)
            print(f"Request failed with status code {response.status_code}")
            return None, f"Request failed, please check Figma link and allow anyone with the link view file"

        log("Processed figma link", figma_file=key)

        return figma_file_object, None

    """ READ SERVICE """

    # async def read_all() -> list[UserBM]:
    #     """Get all users from database and return them as a list"""
    #     return await UserDAO.read_all()

    async def convert_to_dom(figma_file_key: str):
        log("Convert to DOM request", figma_file=figma_file_key)

        """ run request to figma-to-dom service and return result """
        json_file_path = pathlib.Path(config.DATA_DIR_FIGMA_FILES).joinpath(figma_file_key).joinpath("file.json")
        if not fs.is_file_exist(json_file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Figma file not found",
            )

        return await make_convert_request(figma_file_key)

    # # async def read_specific(id: OID) -> UserBM:
    # #     """Get specific user from database and return"""
    # #     return await UserDAO.read(id=id)

    # async def read_specific(username: Username) -> UserBM:
    #     """Get specific user by username and return"""
    #     return await UserDAO.get_by_username(username)

    # async def read_featured() -> list[UserBM]:
    #     """Get featured users from database and return them as a list"""
    #     return await UserDAO.read_featured()

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

    # """ DELETE SERVICE """

    # async def delete(username: Username, token: UserTokenBM):
    #     """Delete user from database"""

    #     user = await UserDAO.get_by_username(username)

    #     if str(user.id) != str(token.id):
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not allowed")

    #     # Delete all user photos from db
    #     # _ = await PhotoDAO.collection.delete_many({"owner": user.id})

    #     # Delete all user photos from disk

    #     result = await UserDAO.delete(id=user.id)
    #     log(f'User "{ user.username }" has been deleted', level="warning")
    #     return result
