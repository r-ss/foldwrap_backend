import httpx

from config import config
from log import log
from models.email import EmailBM


class EmailService:
    async def send_email(email: EmailBM):
        if email.recipient.startswith("testuser"):
            log("Email sending skipped because of test user case", email_to=email.recipient)
            return

        log("Sending email", email=email)

        email.template_model["product_name"] = config.PROJECT_NAME
        email.template_model["product_url"] = config.HOST

        # Send Postmark API send email request with httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.postmarkapp.com/email/withTemplate",
                headers={
                    "X-Postmark-Server-Token": config.POSTMARK_SERVER_TOKEN,
                },
                json={
                    "From": email.sender,
                    "To": email.recipient,
                    "TemplateAlias": str(email.type),
                    "TemplateModel": email.template_model,
                },
            )

        sending_result = response.json()

        if sending_result["ErrorCode"] == 0:
            log("Email sent", result=sending_result)
        else:
            log("Email sending error", error=sending_result["Message"], level="error")
