import pathlib

import pytest

from config import config
from tests.testutils import delete, get, patch, postFiles


@pytest.mark.anyio
async def test_photo_unsupported_format(client, alice):
    """TEST BAD FORMAT FILE"""
    bad = pathlib.Path(config.TESTING_ASSETS_PATH).joinpath("book.txt")
    status_code, result = await postFiles(client, "/photo", [str(bad)], auth=alice.token)
    assert status_code == 422
    assert result["detail"] == "Only PNG and JPEG formats are allowed"


@pytest.mark.anyio
async def test_photos_multiple_upload(client, alice):
    """UPLOAD MULTIPLE"""

    file1 = pathlib.Path(config.TESTING_ASSETS_PATH).joinpath("photos").joinpath("IMG_9949.jpeg")
    file2 = pathlib.Path(config.TESTING_ASSETS_PATH).joinpath("photos").joinpath("DALLE - panorama of the american Wild West with desert and mountains.png")

    status_code, result = await postFiles(client, "/photo", [str(file1), str(file2)], auth=alice.token)
    assert status_code == 201

    """ NOW DELETE THEM """

    for id in [result[0]["id"], result[1]["id"]]:
        status_code, result = await delete(client, f"/photo/{id}", auth=alice.token)
        assert status_code == 200


@pytest.mark.anyio
async def test_photo_upload(client, bob):
    """UPLOAD"""
    file = pathlib.Path(config.TESTING_ASSETS_PATH).joinpath("photos").joinpath("IMG_9949.jpeg")
    status_code, result = await postFiles(client, "/photo", str(file), auth=bob.token)
    assert status_code == 201
    id1 = result[0]["id"]

    filename = result[0]["metadata"]["filename"].split(".")[0]

    """ BOB NOW MUST HAVE A COVER PHOTO FIELD """
    status_code, result = await get(client, f"/user/{bob.username}")
    assert status_code == 200
    assert result["cover_photo"] == filename

    """ GET SPECIFIC """
    for _ in range(10):  # firing multiple times to test redis cache
        status_code, result = await get(client, f"/photo/{id1}", auth=bob.token)
        assert status_code == 200
        assert result["featured"] is True

    """UPLOAD SECOND PHOTO"""
    file = pathlib.Path(config.TESTING_ASSETS_PATH).joinpath("photos").joinpath("DALLE - panorama of the american Wild West with desert and mountains.png")
    status_code, result = await postFiles(client, "/photo", str(file), auth=bob.token)
    assert status_code == 201
    id2 = result[0]["id"]

    """ CHECK IT'S NOT FEATURED """
    status_code, result = await get(client, f"/photo/{id2}", auth=bob.token)
    assert status_code == 200
    assert result["featured"] is False

    """MARK AS FEATURED """
    status_code, result = await patch(client, f"/photo/{id2}/feature", auth=bob.token)
    assert status_code == 200

    status_code, result = await get(client, f"/photo/{id2}", auth=bob.token)
    assert status_code == 200
    assert result["featured"] is True

    """ FIRST PHOTO MUST NOT BE FEATURED NOW """
    status_code, result = await get(client, f"/photo/{id1}", auth=bob.token)
    assert status_code == 200
    assert result["featured"] is False

    """ GET ALL FOR USER """
    status_code_all, result_all = await get(client, f"/user/{bob.username}/photos", auth=bob.token)
    assert status_code_all == 200

    """ DELETE SECOND PHOTO """
    status_code, result = await delete(client, f"/photo/{id2}", auth=bob.token)
    assert status_code == 200

    """ FIRST PHOTO MUST BE FEATURED NOW """
    status_code, result = await get(client, f"/photo/{id1}", auth=bob.token)
    assert status_code == 200
    assert result["featured"] is True

    """ DELETE FIRST PHOTO """
    status_code, result = await delete(client, f"/photo/{id1}", auth=bob.token)
    assert status_code == 200

    """ BOB MUST NOT HAVE PHOTOS NOW """
    status_code_all, result_all = await get(client, f"/user/{bob.username}/photos", auth=bob.token)
    assert status_code_all == 200
    assert result_all == []

    status_code, result = await get(client, f"/user/{bob.username}", auth=bob.token)
    assert status_code == 200
    assert result["cover_photo"] is None


# @pytest.mark.anyio
# async def test_user_userpic_generated_paths():
#     user = UserBM(username="piska55", _id="63edeb36079b88b65fef7a7b", userhash="hehe", userpic="36feb6126db327e5")
#     dict = user.dict()
#     dict["_id"] = dict["id"]
#     userRender = UserRenderBM.parse_obj(dict)
#     assert userRender.dict()["userpic"] == {
#         "url_150": f"/piska55/userpic/36feb6126db327e5_150.jpg",
#         "url_512": f"/piska55/userpic/36feb6126db327e5_512.jpg",
#     }
