import websockets


from fastapi import HTTPException, status

from models.figma_file import FigmaFileLinkBM
from dao.dao_figma_file import FigmaFileDAOLayer


from pydantic import BaseModel
from models.figma_file import FigmaLink

# from fastapi.responses import JSONResponse
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from services.figma import FigmaService

from log import log

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

FigmaFileDAO = FigmaFileDAOLayer()


router = InferringRouter(tags=["Figma"])


""" Websocket solution to show real-time progress of figma file processing
    We send request from frontend not as POST request, by via websocket instead,
    processing a file and sending progress update
"""

figmawebsocketrouter = APIRouter()


class FigmaFileWebsockerRequestBM(BaseModel):
    """Used in websocket_endpoint_ticker to validate incoming data"""

    command: str
    date_string: str
    link: FigmaLink


@figmawebsocketrouter.websocket("/ws/figma/process/{date_string}")
async def websocket_endpoint_ticker(date_string: str, websocket: WebSocket):
    async def on_connect():
        log("figma_ws_process connected")
        await websocket.accept()

    async def on_receive(data):
        # websocket receive event
        log("figma_ws_process received data", data=data)
        parsed = FigmaFileWebsockerRequestBM.parse_raw(data)
        # await websocket.send_text(f"Message text was: {data}")
        # await send_update({"message": f"hello stranger, {date_string}"})
        return parsed

    async def send_update(data):
        # websocket receive event
        log("figma_ws_process sending update", data=data)
        # await websocket.send_text(f"Message text was: {data}")
        await websocket.send_json(data)

    async def on_disconnect():
        log("figma_ws_process websocket disconnected")
        # websocket diconnect event
        pass

    try:
        await on_connect()
        while True:
            data = await websocket.receive_text()

            # print(figma_link)
            # print(type(figma_link))

            await send_update({"progress": 1, "error": False, "done": False, "message": "starting..."})

            try:
                parsed_data = await on_receive(data)
                figma_link = FigmaFileLinkBM(link=parsed_data.link)
            except ValueError as _:
                await send_update({"progress": 100, "error": True, "done": False, "message": "Invalid figma link recieved"})
                await on_disconnect()
                break

            figma_service_status = await FigmaService.get_status()
            if figma_service_status["result"] != "service ok":
                await send_update({"progress": 100, "error": True, "done": False, "message": "figma service connection error"})
                await on_disconnect()
                break

            # Fake routine
            # await asyncio.sleep(1.7)
            # await send_update({"progress": 20, "error": False, "done": False, "message": "downloading figma..."})
            # await asyncio.sleep(1.6)
            # await send_update({"progress": 40, "error": False, "done": False, "message": "downloading images..."})
            # await asyncio.sleep(1.7)
            # await send_update({"progress": 90, "error": False, "done": False, "message": "buildind banner..."})
            # await asyncio.sleep(1)
            # # await send_update({"progress": 95, "error": True, "done": False, "message": "We are fucked up"})
            # await send_update({"progress": 100, "error": False, "done": True, "message": "Complete", "redirect_to_key": "atata"})

            # Real routine
            await send_update({"progress": 10, "error": False, "done": False, "message": "downloading figma design"})
            process_result, error_result = await FigmaService.process_figma_link(figma_link)

            if error_result:
                await send_update({"progress": 100, "error": True, "done": False, "message": error_result})
                await on_disconnect()
                break

            await send_update({"progress": 45, "error": False, "done": False, "message": "downloading assets..."})
            convert_result = await FigmaService.convert_to_dom(process_result.figma_file_key)

            if convert_result["resource"] == "figma_to_dom":
                # saving FigmaFileBM to database

                # figmafile = FigmaFileBM(
                #     figma_file_key = process_result.figma_file_key,
                #     json_downloaded = datetime.utcnow(),
                #     comment = "created in websocket views/figma",
                # )

                # figmafile_db = await FigmaFileDAO.create(figmafile)

                # print(figmafile_db)

                await send_update({"progress": 100, "error": False, "done": True, "message": "ready...", "redirect_to_key": process_result.figma_file_key})
            else:
                await send_update({"progress": 100, "error": True, "done": False, "message": "Unexpected convertion result"})
                await on_disconnect()
                break

            # log("finished")
            await on_disconnect()

    except WebSocketDisconnect:
        log("WebSocketDisconnect")
        await on_disconnect()
    except websockets.exceptions.ConnectionClosedOK:
        log("ConnectionClosedOK")
        pass


@cbv(router)
class FigmaCBV:

    """CREATE"""

    @router.get("/figma/status", status_code=status.HTTP_200_OK)
    async def figma_status(self):
        """Checking status of figma service"""
        return await FigmaService.get_status()

    # @router.post("/figma/process", status_code=status.HTTP_201_CREATED)
    # async def figma_process(self, figma_link: FigmaFileLinkBM):
    #     return await FigmaService.process_figma_link(figma_link)

    # @router.post("/figma/initiate", status_code=status.HTTP_201_CREATED)
    # async def figma_initiate(self, figma_link: FigmaFileLinkBM):
    #     return await FigmaService.process_figma_link(figma_link)

    @router.get("/figma/editor/{figma_file_key}", status_code=status.HTTP_200_OK)
    async def edit_figma_file(self, figma_file_key: str):
        try:
            key = FigmaFileLinkBM(link=figma_file_key).link
        except Exception as _:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid figma key",
            )

        result = await FigmaService.convert_to_dom(key)
        return result
