import os
from hashlib import blake2b

import pytest

from config import config
from dao.ress_redis import RessRedisAbstraction
from log import log
from tests.testutils import get


@pytest.mark.anyio
async def test_debug_mode(client):
    if config.PRODUCTION:
        assert config.DEBUG is False
    else:
        assert config.DEBUG is True


@pytest.mark.anyio
async def test_testing_mode(client):
    assert config.TESTING_MODE is True


@pytest.mark.anyio
async def test_is_redis_running():
    redis = RessRedisAbstraction()
    if not redis.ping():
        log("Redis is not running.", level="warning")


@pytest.mark.anyio
async def test_secrets():
    assert config.SECRET_KEY.startswith("foldsecret") is True


@pytest.mark.anyio
async def test_filesystem():
    testfile_path = os.path.join(config.TESTING_ASSETS_PATH, "lambo.png")
    assert os.path.isfile(testfile_path) is True
    h = blake2b(digest_size=config.HASH_DIGEST_SIZE)
    h.update(open(testfile_path, "rb").read())
    assert h.hexdigest() == "011651d77cf25898"


@pytest.mark.anyio
async def test_root(client):
    status_code, result = await get(client, "/")
    assert status_code == 404


@pytest.mark.anyio
async def test_info(client):
    status_code, result = await get(client, "/info")
    assert status_code == 200
    assert result["resource"] == config.PROJECT_NAME.lower()
    assert result["testing"] is True
    assert result["python version"].startswith("3.12") is True
