import pytest
from httpx import AsyncClient

from config import config
from main import app
from tests.testutils import postForm


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    config.TESTING_MODE = True
    async with AsyncClient(app=app, base_url="http://test") as client:
        # print("Client is ready")
        yield client


alice_save = bob_save = jesus_save = None


class LoggedInTestUser:
    """Represents logged-in test user, used only in tests"""

    def __init__(self, id: str, email: str, token: str, refresh_token: str) -> None:
        self.id: str = id
        self.email: str = email
        self.token: str = token
        self.refresh_token = refresh_token


@pytest.fixture
async def alice(client):
    global alice_save

    if not alice_save:  # send login request only on first call
        login_data = {
            "username": "alice@foldwrap.com",
            "password": config.TESTUSER_ALICE_PASSWORD,
        }
        status_code, result = await postForm(client, "/token", login_data)
        alice_save = LoggedInTestUser(
            result["user"]["id"],
            result["user"]["email"],
            result["access_token"],
            result["refresh_token"],
        )

    return alice_save


@pytest.fixture
async def bob(client):
    global bob_save

    if not bob_save:  # send login request only on first call
        login_data = {
            "username": "bob@foldwrap.com",
            "password": config.TESTUSER_BOB_PASSWORD,
        }
        status_code, result = await postForm(client, "/token", login_data)
        bob_save = LoggedInTestUser(
            result["user"]["id"],
            result["user"]["email"],
            result["access_token"],
            result["refresh_token"],
        )

    return bob_save


@pytest.fixture
async def jesus(client):
    global jesus_save

    if not jesus_save:  # send login request only on first call
        login_data = {
            "username": "jesus@foldwrap.com",
            "password": config.TESTUSER_JESUS_PASSWORD,
        }
        status_code, result = await postForm(client, "/token", login_data)
        jesus_save = LoggedInTestUser(
            result["user"]["id"],
            result["user"]["email"],
            result["access_token"],
            result["refresh_token"],
        )

    return jesus_save
