import pytest

from services.misc.utils import make_random_string
from tests.testutils import delete, get, post, postForm


@pytest.mark.anyio
async def test_users_get_all(client):
    status_code, result = await get(client, "/users")
    assert status_code == 200


@pytest.mark.anyio
async def test_user_bad_input(client):
    # No password provided
    data = {"email": "some@domain.com"}
    status_code, result = await post(client, "/users", data)
    assert result["detail"] == "Email and password must be provided for registration"
    # assert status_code == 422  # HTTP_400_BAD_REQUEST
    # Short password case
    data = {"email": "some@domain.com", "password": "short"}
    status_code, result = await post(client, "/users", data)
    assert result["detail"].startswith("Password must at least 6 char") is True
    assert status_code == 400  # HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_user_crud(client):
    """COUNT"""
    status_code, result = await get(client, "/users")
    users_count = len(result)
    assert status_code == 200

    id = None
    email = f"testuser_{make_random_string(4).casefold()}@foldwrap.com"
    password = make_random_string(6)
    token = None

    user_data = {"email": email, "password": password}
    login_data = {"username": email, "password": password}

    """ CREATE """
    status_code, result = await post(client, "/users", user_data)

    id = result["id"]
    email = result["email"]
    assert result["email"] == email
    assert result["userhash"] == "******"
    assert status_code == 201  # HTTP_201_CREATED

    """ CREATE DUPLICATE """
    status_code, result = await post(client, "/users", user_data)
    assert status_code == 409  # 409 - Conflict
    assert result["detail"] == "User with this email already registered"

    """ READ """

    status_code, result = await get(client, f"/user/{id}")

    assert status_code == 200
    assert result["email"] == email
    assert result["id"] == id
    assert result["userhash"] == "read - censored in dao"
    assert result["registered_via"] == "web"
    assert result["created_ip"]["x_real_ip"] == "88.88.88.100"
    assert result["created_ip"]["x_forwarded_for"] == "88.88.88.200"

    """ LOGIN """

    status_code, result = await postForm(client, "/token", login_data)
    token = result["access_token"]
    assert status_code == 202

    # """ UPDATE - change of username disabled for now"""

    # data = {"id": id, "username": "prefix" + username}
    # status_code, result = await patch(client, f"/users/{id}", data, auth=token)
    # assert result["username"] == "prefix" + username
    # assert status_code == 200

    """ DELETE """

    status_code, result = await delete(client, f"/user/{id}", auth=token)
    # assert status_code == 200  # HTTP_200_OK
    assert result["result"] == f"user {id} deleted"

    """ COUNT AGAIN """

    status_code, result = await get(client, "/users")
    assert users_count == len(result)
