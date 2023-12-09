import hashlib
import hmac
from fastapi import Header, HTTPException, status, Request
from typing import Optional

from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from services.subscription import SubscriptionService

from services.misc.utils import send_message

from log import log

from pydantic import BaseModel


from config import config


class LemonSqueezyWebhookPayloadBM(BaseModel):
    # Define the expected fields
    # https://docs.lemonsqueezy.com/help/webhooks
    meta: dict
    data: dict


router = InferringRouter(tags=["Subscription"])


@cbv(router)
class SubscriptionCBV:

    """Lemon Squeezy Webhook handler"""

    @router.post("/lemonsqueezy_wbhk", status_code=status.HTTP_200_OK)
    async def lemonsqueezy_webhook(self, payload: LemonSqueezyWebhookPayloadBM, request: Request, x_signature: Optional[str] = Header(None)):
        """A POST request will be sent to this URL every time an event is triggered in Lemon Squeezy
        https://docs.lemonsqueezy.com/help/webhooks#signing-requests

        """

        if x_signature is None:
            raise HTTPException(status_code=400, detail="X-Signature header missing")

        body_bytes = await request.body()
        digest = hmac.new(key=config.LEMONSQUEEZY_SECRET.encode(), msg=body_bytes, digestmod=hashlib.sha256).hexdigest()

        if not hmac.compare_digest(digest, x_signature):
            raise HTTPException(status_code=401, detail="Invalid X-Signature")

        """ After comparing the signatures, the request is considered authentic. Proceed with the rest of the function. """

        # print(payload)
        # print("========================")

        test_mode = payload.meta.get("test_mode", False)
        event_name = payload.meta["event_name"]
        status = payload.data["attributes"]["status"]
        customer_email = payload.data["attributes"]["user_email"]

        send_message(f"Lemon Squeezy webhook received\nevent: {event_name}\nstatus: {status}\ncustomer: {customer_email}\ntest_mode: {test_mode}")

        match event_name:
            case "subscription_created":
                result = await SubscriptionService.subscribe_user(payload)
                log("Subscription created", email=customer_email)
                return result

            case "subscription_payment_success":
                result = await SubscriptionService.update_subscription(payload)
                log("Subscription payment success", email=customer_email)
                return result
            case _:
                if status == "expired":
                    result = await SubscriptionService.unsubscribe_user(payload)
                    log("Subscription expired", email=customer_email)
                    return result
                else:
                    result = await SubscriptionService.update_subscription(payload)
                    log("Subscription updated", event_name=event_name, email=customer_email)
                    return result

        return {"message": "Valid signature, no action taken"}
