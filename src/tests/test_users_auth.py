import pytest

from config import config
from tests.testutils import get, patch, postForm


@pytest.mark.anyio
async def test_6digits_code(client):
    # for code in ["000000", "123456", "999999"]:
    #     status_code, result = await get(client, f"/confirm?code={code}")
    #     assert status_code == 200

    # for code in ["0000001", "abcdef", "&*^%$#"]:
    #     status_code, result = await get(client, f"/confirm?code={code}")
    #     assert status_code == 400

    pass


@pytest.mark.anyio
async def test_auth_login_uppercase(client):
    data = {"username": "BOB@FOLDWRAP.COM", "password": config.TESTUSER_BOB_PASSWORD}
    status_code, result = await postForm(client, "/token", data)
    assert status_code == 202


@pytest.mark.anyio
async def test_auth_login_post_as_form(client):
    data = {
        "username": "bob@foldwrap.com",
        "password": config.TESTUSER_BOB_PASSWORD,
    }

    status_code, result = await postForm(client, "/token", data)
    # print(result)

    assert result["token_type"] == "bearer"

    assert result["user"]["email"] == "bob@foldwrap.com"
    assert result["user"]["last_login_ip"]["x_real_ip"] == "88.88.88.100"
    assert result["user"]["last_login_ip"]["x_forwarded_for"] == "88.88.88.200"
    assert result["user"]["comment"] == "****"
    assert result["user"]["userhash"] == "******"
    assert status_code == 202

    # """ Obtain refresh token with request with JSON """
    refresh_token_data = {"refresh_token": result["refresh_token"]}
    status_code, result_json = await patch(client, "/token", refresh_token_data)
    # print(result_json)


# @pytest.mark.anyio
# async def test_auth_refresh_token(client):
#     data = {
#         "username": f"bob@{config.DOMAIN}",
#         "password": config.TESTUSER_BOB_PASSWORD,
#     }
#     status_code, result = await postForm(client, "/refreshtoken", data)
#     print(result)
#     assert result["token_type"] == "bearer"
#     assert status_code == 202


# @pytest.mark.anyio
# async def test_auth_bad_login(client):
#     data = {"username": "sh@bad", "password": "wrong-password"}  # too short
#     status_code, result = await postForm(client, "/token", data)
#     assert result["detail"].startswith("Username must be at least 3 char") is True
#     assert status_code == 400


# @pytest.mark.anyio
# async def test_auth_bad_password(client):
#     data = {"username": "Alice", "password": "wrong-password"}
#     status_code, result = await postForm(client, "/token", data)
#     assert result["detail"] == "Wrong password"
#     assert status_code == 401


# def test_auth_secret_page_via_auth_header(client):
#     status_code, result = get(client, '/secretpage', headers={'Authorization': 'bearer ' + token_save})
#     assert status_code == 200
#     assert result['message'] == 'this is secret message'


@pytest.mark.anyio
async def test_auth_secret_page_via_fixture(client, alice):
    status_code, result = await get(client, "/secretpage", auth=alice.token)
    assert status_code == 200
    assert result["message"] == "this is secret message"


@pytest.mark.anyio
async def test_auth_secret_page_with_expired_token(client):
    expired_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTY1OTcxMTYsImlhdCI6MTY5NjU5NjM5Niwic2NvcGUiOiJhY2Nlc3NfdG9rZW4iLCJlbWFpbCI6ImFsaWNlQGZvbGR3cmFwLmNvbSIsImlkIjoiNjUxZWI0ODllNGNkZDQwZGI2ZWJhZDk2IiwiaXNfc3VwZXJhZG1pbiI6ZmFsc2V9.mqttel0JABUgojXVYN1030jAlhv2ZUmHSIx8zBfSe2Q"
    status_code, result = await get(client, "/secretpage", auth=expired_access_token)
    assert status_code == 401
    assert result["detail"] == "Error decoding token (Signature Expired)"


@pytest.mark.anyio
async def test_obtain_new_refresh_token(client, alice):
    """Obtain new pair of tokens using refresh_token"""

    refresh_token_data = {"refresh_token": alice.refresh_token}
    status_code, result = await patch(client, "/token", refresh_token_data)
    obtained_access_token = result["access_token"]

    status_code, result = await get(client, "/secretpage", auth=obtained_access_token)
    assert status_code == 200
    assert result["message"] == "this is secret message"
