import pytest

from config import config
from services.misc.utils import make_random_string
from tests.testutils import post, postForm


@pytest.mark.anyio
async def test_user_password_reset(client):
    """Unregistered email case"""
    status_code, result = await post(client, "/user/password_forgot", {"email": "unregistered@example.co"})
    assert status_code == 400
    assert result["detail"] == "User with this email is not registered"

    """ Registered email case """
    status_code, result = await post(client, "/user/password_forgot", {"email": f"bob@{config.DOMAIN}"})
    assert status_code == 201

    token = result["readable_token_for_testing"]

    data = {"email": f"bob@{config.DOMAIN}", "reset_token": token, "new_password": make_random_string(10)}

    """ Request reset """
    status_code, result = await post(client, "/user/password_reset", data)

    """ Trying to login with old password """
    authdata = {"username": f"bob@{config.DOMAIN}", "password": config.TESTUSER_BOB_PASSWORD}
    status_code, result = await postForm(client, "/token", authdata)
    assert status_code == 401

    """ Trying to login with new password """
    newauthdata = {"username": f"bob@{config.DOMAIN}", "password": data["new_password"]}
    status_code, result = await postForm(client, "/token", newauthdata)
    assert status_code == 202

    """ Requesting password change token again to change password back to Bob's default """
    status_code, result = await post(client, "/user/password_forgot", {"email": f"bob@{config.DOMAIN}"})
    assert status_code == 201

    second_token = result["readable_token_for_testing"]
    data = {"email": f"bob@{config.DOMAIN}", "reset_token": second_token, "new_password": config.TESTUSER_BOB_PASSWORD}
    status_code, result = await post(client, "/user/password_reset", data)

    """ Trying to login with Bob's default password """
    newauthdata = {"username": f"bob@{config.DOMAIN}", "password": config.TESTUSER_BOB_PASSWORD}
    status_code, result = await postForm(client, "/token", newauthdata)
    assert status_code == 202
