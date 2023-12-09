from pathlib import Path

from fastapi import status, Request
from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter


from config import config


router = InferringRouter(tags=["Temp Utilities"])


from pydantic import BaseModel


class TestBM(BaseModel):
    testfield: str


@cbv(router)
class TempUtilitiesCBV:
    # @router.get("/listaigirls")
    # async def list_aigirls(self):
    #     aigirlsdir = Path(config.BASE_DIR).parent.joinpath("frontend/public/gfx/ai-girls")

    #     pictures = fs.list_visible_files(aigirlsdir)

    #     return JSONResponse(
    #         status_code=status.HTTP_200_OK,
    #         content={"resource": "kaka", "BASE_DIR": config.BASE_DIR, "aigirlsdir": str(aigirlsdir), "pictures": pictures},
    #     )

    @router.post("/testform", status_code=status.HTTP_201_CREATED)
    async def testform(self, request: Request, item: TestBM):
        print("request headers", request.headers)
        print("item", item)

        return {"result": "unknown --"}
