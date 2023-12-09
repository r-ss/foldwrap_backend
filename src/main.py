from fastapi import APIRouter, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient


from config import config
from log import log
from services.misc.utils import send_message

from views.figma import router as figma_router
from views.figma import figmawebsocketrouter  # enables websocket communication


from views.info import router as info_router

# from views.maintenance.auth_log import router as auth_log_router
from views.export import router as export_router
from views.user.password_reset import router as user_passwordreset_router
from views.subscription import router as user_subscription_router
from views.users_auth import router as users_auth_router
from views.users_crud import router as users_crud_router
from views.feedback import router as feedback_router

from views.temp_utilities import router as temp_utilities_router

if config.PRODUCTION:
    import sentry_sdk

    sentry_sdk.init(
        dsn="https://0290b328096ca32d74610abe1089f72b@o4506050766045184.ingest.sentry.io/4506050769649664",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.75,
    )

mainrouter = APIRouter(prefix="/api/v1")

routers = [info_router, users_auth_router, users_crud_router, user_passwordreset_router, figma_router, export_router, user_subscription_router, feedback_router, temp_utilities_router]

app = FastAPI(
    docs_url="/autodoc",  # not default
    redoc_url=None,
    openapi_url="/api/v1/openapi_schema.json",  # not default
    title=config.PROJECT_NAME,
    # description=description,
    version="0.0.1",
)
testclient = TestClient(app)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def app_startup_event():
    log("App started", level="debug")
    send_message("Started")


@app.get("/", tags=["General"])
def read_root():
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There is no root url")


# including routes from our views
for r in routers:
    mainrouter.include_router(r)  # to enable prefix
    app.include_router(mainrouter)

app.include_router(figmawebsocketrouter)  # to enable websocket communication
