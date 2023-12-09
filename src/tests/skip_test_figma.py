import pytest

from tests.testutils import post


@pytest.mark.anyio
async def test_figma(client):
    goodlinks = [
        "https://www.figma.com/file/tAXXaJWhOsIbDK4opaDSRz/Untitled?type=design&node-id=0-1&mode=design&t=Oy2wxvsWWWTM55O1-0",
        "https://www.figma.com/file/tAXXaJWhOsIbDK4opaDSRz/Untitled?type=design&node-id=0%3A1&mode=design&t=Oy2wxvsWWWTM55O1-1",
        "https://www.figma.com/file/tAXXaJWhOsIbDK4opaDSRz/",
        "tAXXaJWhOsIbDK4opaDSRz",
    ]

    badlinks = [
        "https://turnislefthome.com/twitch-2014-retrospective-illustrations",
        "https://app.spline.design/file/9a1aad08-3700-4db7-9e89-1d495733422c",
        "https://vercel.com",
        "https://www.figma.com/files/recents-and-sharing/recently-viewed?fuid=1015608006678319223",
    ]

    for link in goodlinks:
        data = {"link": link}
        status_code, result = await post(client, "/figma/link", data)
        assert status_code == 201
        # print(status_code, result)

    for link in badlinks:
        data = {"link": link}
        status_code, result = await post(client, "/figma/link", data)
        assert status_code == 422
        # print(status_code, result)
