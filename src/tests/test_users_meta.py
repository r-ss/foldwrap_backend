import pytest

from tests.testutils import get


@pytest.mark.anyio
async def test_user_get_alice(client, alice):
    status_code, result = await get(client, f"/user/{alice.id}")
    assert status_code == 200
    assert result["id"] == alice.id
    assert result["email"] == "alice@foldwrap.com"
    assert result["userhash"] == "read - censored in dao"
    assert result["is_superadmin"] is False


@pytest.mark.anyio
async def test_user_get_bob(client, bob):
    status_code, result = await get(client, f"/user/{bob.id}")
    assert status_code == 200
    assert result["id"] == bob.id
    assert result["email"] == "bob@foldwrap.com"
    assert result["userhash"] == "read - censored in dao"
    assert result["is_superadmin"] is False


@pytest.mark.anyio
async def test_user_get_jesus(client, jesus):
    status_code, result = await get(client, f"/user/{jesus.id}")
    assert status_code == 200
    assert result["id"] == jesus.id
    assert result["email"] == "jesus@foldwrap.com"
    assert result["userhash"] == "read - censored in dao"
    assert result["is_superadmin"] is True
