import pytest

from config import config
from tests.testutils import post


@pytest.mark.anyio
async def test_create_test_users(client):
    login_data = {"email": "alice@foldwrap.com", "password": config.TESTUSER_ALICE_PASSWORD}
    status_code, result = await post(client, "/users", login_data)

    print(result)

    assert result["email"] == "alice@foldwrap.com"
    assert status_code == 201  # HTTP_201_CREATED

    login_data = {"email": "bob@foldwrap.com", "password": config.TESTUSER_BOB_PASSWORD}
    status_code, result = await post(client, "/users", login_data)
    assert result["email"] == "bob@foldwrap.com"
    assert status_code == 201  # HTTP_201_CREATED

    login_data = {"email": "jesus@foldwrap.com", "password": config.TESTUSER_JESUS_PASSWORD}
    status_code, result = await post(client, "/users", login_data)
    assert result["email"] == "jesus@foldwrap.com"
    assert status_code == 201  # HTTP_201_CREATED

    print("Make jesus superadmin manually")
