import asyncio
import pathlib

import httpx
import pytest

from config import config
from log import log
from models.figma_file import ImagesLinksModel
from services.misc.filesystem import FileSystemUtils

fs = FileSystemUtils()


async def download_file(url, out_dir: pathlib.Path, key) -> (str, bool):
    # can return False if errored or str - downloaded filename
    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code == 200:
            # Get the Content-Type header
            content_type = response.headers.get("content-type")
            # set file extension
            extension = "jpeg"
            match content_type:
                case "image/png":
                    extension = "png"
                case _:
                    extension = "jpeg"

            fs.check_dir(out_dir)
            file_path = out_dir.joinpath(f"{key}.{extension}")

            with open(file_path, "wb") as file:
                file.write(response.content)
                return f"{key}.{extension}"
            # print(f"File downloaded to {file_path}")
            # print(f"Content-Type: {content_type}")
        else:
            log(f"Failed to download the file. Status code: {response.status_code}")
            return False


@pytest.mark.anyio
async def test_figma_images(client):
    key = "tAXXaJWhOsIbDK4opaDSRz"
    # key = 'LPFvNCgljdnH9PnW1epn7B'
    json_file = pathlib.Path(config.UPLOADS_DIR_FIGMA_FILES).joinpath(key).joinpath("images.json")

    out_dir = pathlib.Path(config.UPLOADS_DIR_FIGMA_FILES).joinpath("out")
    fs.check_dir(out_dir)

    tasks = []

    with open(json_file, "r") as f:
        # data = json.load(f)
        # print(type(f.read()))

        obj = ImagesLinksModel.parse_raw(f.read())

        # print(type(obj))
        for key, value in obj.meta.images.items():
            print(f"Key: {key}, Value: {value}")
            task = download_file(str(value), out_dir, key)
            tasks.append(task)

    results = await asyncio.gather(*tasks)
    print("Download results:", results)
