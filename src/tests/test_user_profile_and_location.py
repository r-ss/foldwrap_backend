import pytest

from services.misc.utils import make_random_string
from tests.testutils import patch


@pytest.mark.anyio
async def test_user_fill_profile(client, alice):
    profile_data = {"sex": "female", "name": "Alice", "birth": "1997-03-22", "about": f"Hola from test user Alice, {make_random_string(4)}"}

    """ FILL PROFILE """
    status_code, result = await patch(client, "/user/profile", profile_data, auth=alice.token)

    assert result["email"] == alice.email
    assert result["id"] == alice.id
    assert result["userhash"] == "******"
    assert result["profile"]["about"] == profile_data["about"]
    assert status_code == 200  # HTTP_200_OK
