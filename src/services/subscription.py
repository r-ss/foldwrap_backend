import httpx
from datetime import datetime

# from models.misc.lemonsqueezy import LemonsqueezyLicenseKeyBM
from models.user import UserProfileBM

from dao.dao_user import UserDAOLayer

from config import config
from log import log
from models.lemonsqueezy.subscription_details import SubscriptionDetailsBM

UserDAO = UserDAOLayer()


class SubscriptionService:
    def parse_sub_details(subscription_details: dict):
        try:
            d = SubscriptionDetailsBM.parse_obj(subscription_details["attributes"])
            d.subscription_id = subscription_details["attributes"]["first_subscription_item"]["id"]
            d.customer_portal_url = subscription_details["attributes"]["urls"]["customer_portal"]
        except Exception as err:
            log("Error while parsing subscription details", lever="error", err=err)
            return None
        return d

    async def subscribe_user(payload):
        attributes = payload.data["attributes"]

        customer_email = attributes["user_email"]
        customer_name = attributes["user_name"]

        user = await UserDAO.get_by_email(customer_email)

        if not user.profile and customer_name:
            user.profile = UserProfileBM(name=customer_name, about=None)

        user.paid_status = attributes["status"]
        user.paid_via = "lemonsqueezy"

        user.pro_customer = True
        user.pro_reason = attributes["status"]

        parsed_details = SubscriptionService.parse_sub_details(payload.data)
        if parsed_details:
            user.subscription_details = parsed_details

        updated_user = await UserDAO.update(user)

        return {"result": True, "message": "User subscribed", "user_id": str(updated_user.id)}

    async def update_subscription(payload):
        attributes = payload.data["attributes"]

        customer_email = attributes["user_email"]
        user = await UserDAO.get_by_email(customer_email)

        parsed_details = SubscriptionService.parse_sub_details(payload.data)
        if parsed_details:
            user.subscription_details = parsed_details
            updated_user = await UserDAO.update(user)

            return {"result": True, "message": "User subscription updated", "user_id": str(updated_user.id)}

        # print(type(parsed_details))
        # print(parsed_details)

        return {"result": True, "message": "User subscription not updated", "user_id": str(user.id)}

    async def unsubscribe_user(payload):
        attributes = payload.data["attributes"]

        customer_email = attributes["user_email"]

        user = await UserDAO.get_by_email(customer_email)

        user.paid_status = attributes["status"]

        user.pro_customer = False
        user.pro_reason = None

        parsed_details = SubscriptionService.parse_sub_details(payload.data)
        if parsed_details:
            user.subscription_details = parsed_details

        updated_user = await UserDAO.update(user)

        return {"result": True, "message": "User unsubscribed", "user_id": str(updated_user.id)}
