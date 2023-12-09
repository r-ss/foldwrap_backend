import random
import re
from unicodedata import normalize
import string
import httpx
from config import config


def make_random_string(ln):
    return "".join([random.choice(string.ascii_letters) for i in range(ln)])


def send_message(message):
    if not config.PRODUCTION:  # Don't bother on autotests and in dev mode
        return None

    try:
        with httpx.Client() as client:
            data = {"message": f"{config.PROJECT_NAME}: {message}", "silent": False}
            _ = client.post(config.NOTIFICATIONS_URL, data=data)
    except Exception as err:
        print("Cannot send telegram message due to exception", err)
        pass


def send_bot_message(text):
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        "chat_id": 95622548,  # ress
        "text": text,
    }

    try:
        with httpx.Client() as client:
            response = client.post(url, params=params)
            response.raise_for_status()
            result = response.json()
            if not result["ok"]:
                print(f"Error sending message: {result['description']}")
            else:
                print("Message sent successfully.")
    except httpx.HTTPError as e:
        print(f"HTTP error occurred: {e}")


def slugify(s):
    s = normalize("NFKD", s).encode("ASCII", "ignore").decode("ASCII")
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    return re.sub(r"[-\s]+", "-", s)
