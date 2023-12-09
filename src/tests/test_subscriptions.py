import pytest
import pathlib
import hashlib
import hmac

from config import config

from tests.testutils import get, post


jsons_path = pathlib.Path(config.TESTING_ASSETS_PATH).joinpath("lmnsqz_webhook_test_jsons")


lemonsqueezy_secret = config.LEMONSQUEEZY_SECRET


@pytest.mark.anyio
async def test_subscriptions(client):
    """CREATE SUBSCRIPTION"""

    with open(jsons_path.joinpath("subscription_created.json"), "r") as f:
        payload = f.read()

        """ TEST WITHOUT X-SIGNATURE HEADER """
        status_code, result = await post(client, "/lemonsqueezy_wbhk", payload)
        assert status_code == 400
        assert result["detail"] == "X-Signature header missing"

        """ TEST WITH INVALID X-SIGNATURE """
        headers = {"X-Signature": "some_invalid_signature"}
        status_code, result = await post(client, "/lemonsqueezy_wbhk", payload, headers=headers)
        assert status_code == 401
        assert result["detail"] == "Invalid X-Signature"

        """ TEST WITH VALID X-SIGNATURE """
        digest = hmac.new(key=lemonsqueezy_secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
        headers = {"X-Signature": digest}
        status_code, result = await post(client, "/lemonsqueezy_wbhk", payload, headers=headers)

        assert result["result"] == True
        assert result["message"] == "User subscribed"
        user_id = result["user_id"]

        """ READ USER """
        status_code, result = await get(client, f"/user/{user_id}")
        assert status_code == 200
        assert result["id"] == user_id
        assert result["email"] == "alice@foldwrap.com"
        # assert result["profile"]["name"] == "Matthew Bellamy"
        assert result["pro_customer"] == True
        assert result["pro_reason"] == "on_trial"
        assert result["paid_status"] == "on_trial"
        assert result["paid_via"] == "lemonsqueezy"
        assert result["demo_expires"] == None

        # print(status_code)
        # print(result)

    """ PAY FOR SUBSCRIPTION """

    with open(jsons_path.joinpath("subscription_payment_success.json"), "r") as f:
        payload = f.read()
        digest = hmac.new(key=lemonsqueezy_secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
        headers = {"X-Signature": digest}
        status_code, result = await post(client, "/lemonsqueezy_wbhk", payload, headers=headers)

        # print(status_code)
        # print(result)

    """ UPDATE SUBSCRIPTION """

    with open(jsons_path.joinpath("subscription_updated_valid.json"), "r") as f:
        payload = f.read()
        digest = hmac.new(key=lemonsqueezy_secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
        headers = {"X-Signature": digest}

        status_code, result = await post(client, "/lemonsqueezy_wbhk", payload, headers=headers)

        # print(status_code)
        # print(result)

    """ EXPIRE SUBSCRIPTION """

    with open(jsons_path.joinpath("subscription_updated_expired.json"), "r") as f:
        payload = f.read()
        digest = hmac.new(key=lemonsqueezy_secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
        headers = {"X-Signature": digest}
        status_code, result = await post(client, "/lemonsqueezy_wbhk", payload, headers=headers)

        assert result["result"] == True
        assert result["message"] == "User unsubscribed"
        user_id = result["user_id"]

        """ READ USER """
        status_code, result = await get(client, f"/user/{user_id}")
        assert status_code == 200
        assert result["id"] == user_id
        assert result["email"] == "alice@foldwrap.com"
        # assert result["profile"]["name"] == "Matthew Bellamy"
        assert result["pro_customer"] == False
        assert result["pro_reason"] == None
        assert result["paid_status"] == "expired"
        assert result["paid_via"] == "lemonsqueezy"
        assert result["demo_expires"] == None

        # print(status_code)
        # print(result)
