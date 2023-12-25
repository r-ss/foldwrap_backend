import datetime
import pathlib
import socket
import os  # used only to get run_mode env variable

from pydantic_settings import BaseSettings


RUN_MODE = os.getenv("RUN_MODE", "develomplemt")


PRODUCTION = False
if RUN_MODE == "production":
    PRODUCTION = True


"""
also possible to set run-mode by app's hostname value,
because in production we have predefined docker container with static hostname

if socket.gethostname() == "foldwrap-backend":
    PRODUCTION = True
"""


BASE_DIR_PATH = pathlib.Path.cwd()
SRC_DIR_PATH = pathlib.Path(__file__).parent  # path to this file

DATA_DIR_PATH = SRC_DIR_PATH.parent.parent.joinpath("mount").joinpath("backend_data")
if PRODUCTION:
    DATA_DIR_PATH = pathlib.Path("/data")  # path to data and uploads directory


if BASE_DIR_PATH != SRC_DIR_PATH.parent:
    raise "Check directory sctructure in config.py"


class AppConfig(BaseSettings):
    """Using Pydantic's approach to manage application config
    Docs: https://pydantic-docs.helpmanual.io/usage/settings/
    """

    PROJECT_NAME: str = "Foldwrap"

    # URLs
    DOMAIN: str = "foldwrap.com"
    HOST: str = "https://foldwrap.com"

    # logging setup, more in log.py
    LOG_DIR: str = str(BASE_DIR_PATH.joinpath("logs"))
    LOG_LEVEL: str = "DEBUG"

    # GENERAL SETTINGS AND HOSTS
    BASE_DIR: str = str(BASE_DIR_PATH)
    PRODUCTION: bool = PRODUCTION
    DEBUG: bool = not PRODUCTION
    SECRET_KEY: str = None
    DBHOST: str = None

    REDIS_PASSWORD: str = None
    POSTMARK_SERVER_TOKEN: str = None
    LEMONSQUEEZY_SECRET: str = None

    FIGMA_API_TOKEN: str = None

    TELEGRAM_BOT_TOKEN: str = None

    GOOGLE_OAUTH_CLIENT_ID: str = None
    GOOGLE_OAUTH_SECRET: str = None

    # TESTS
    TESTING_MODE: bool = False  # Must be set to True only in autotests
    TESTING_ASSETS_PATH: str = str(BASE_DIR_PATH.joinpath("testing_assets"))

    # Define passwords for testusers: 2 regular users and 1 admin
    TESTUSER_ALICE_PASSWORD: str = None  # email: alice@foldwrap.com
    TESTUSER_BOB_PASSWORD: str = None  # email: bob@foldwrap.com
    TESTUSER_JESUS_PASSWORD: str = None  # email: jesus@foldwrap.com

    # REDIS_PASSWORD: str
    NOTIFICATIONS_URL: str

    # FORMATTERS
    DATETIME_FORMAT_TECHNICAL: str = "%Y-%m-%d %H:%M:%S"
    DATETIME_FORMAT_HUMAN: str = "%d.%m.%Y %H:%M"

    # AUTHENTICATION
    AUTH_PASSWORD_REGEX: dict = {
        "regex": r"\A[\w\-\.]{6,}\Z",
        "failmessage": "Password must at least 6 characters and may contain . - _ symbols",  # also can be used as hint
    } 
    AUTH_HASHING_ALGORITHM: str = "HS256"  # algorithm to encode/decode JWT user tokens
    AUTH_ACCESS_TOKEN_EXPIRATION_TIME: datetime.timedelta = datetime.timedelta(hours=12)
    AUTH_REFRESH_TOKEN_EXPIRATION_TIME: datetime.timedelta = datetime.timedelta(days=30)

    # PATHS
    DATA_DIR: str = "%s/" % DATA_DIR_PATH
    DATA_DIR_TEMP: str = "%s/temp/" % DATA_DIR_PATH
    DATA_DIR_FIGMA_FILES: str = "%s/figma_files/" % DATA_DIR_PATH

    # MISC
    HASH_DIGEST_SIZE: int = 8  # for hashing files with blake2b

    class Config:
        """Loads the dotenv file."""
        env_file: str = ".env"


config = AppConfig()