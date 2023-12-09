import os
import platform
import socket

# import subprocess
from datetime import datetime

from fastapi import status
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from config import config

# from ress_rabbitmq import RessRabbitMQ

from fastapi import Request


from dao.ress_redis import RessRedisAbstraction
from dao.dao import database_healthcheck

# mq = RessRabbitMQ()

redis = RessRedisAbstraction()

router = InferringRouter(tags=["General"])


@cbv(router)
class InfoCBV:

    """READ"""

    @router.get("/info", summary="Basic system information")
    async def read(self, request: Request):
        """Return basic system information and variables, like is app runs
        in production mode or not. Might be useful on deployment.
        Can be used for fast status check in production

        access via /info url
        """

        load1, load5, load15 = os.getloadavg()

        # redis = RessRedisAbstraction()

        # def get_git_revision_short_hash() -> str:
        #     return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("ascii").strip()
        # try:
        #     git_revision_hash = get_git_revision_short_hash()
        # except Exception as err:
        #     git_revision_hash = f"error {err}"

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "resource": config.PROJECT_NAME.lower(),
                # "git_revision_hash": git_revision_hash,
                "hostname": socket.gethostname(),
                "datetime": datetime.now().strftime("%d %B %Y %H:%M:%S"),
                "os": os.name,
                "platform": platform.system(),
                "platform_release": platform.release(),
                "python version": platform.python_version(),
                "testing": config.TESTING_MODE,
                "production": config.PRODUCTION,
                "redis_ping": redis.ping(),
                "load averages": f"{load1:.2f} {load5:.2f} {load15:.2f}",
                # "rabbitmq_live": mq.ping(),
                "database": await database_healthcheck(),
                "x-real-ip": request.headers.get("X-Real-IP"),
                "x-forwarded-for": request.headers.get("X-Forwarded-For"),
            },
        )
