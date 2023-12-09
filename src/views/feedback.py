from fastapi import status, Depends
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from fastapi.responses import JSONResponse

from models.user import UserTokenBM
from models.feedback import FeedbackEntryBM, FeedbackEntryEditBM

from services.feedback import FeedbackService
from services.users.auth import token_required

from dao.oid import OID

router = InferringRouter(tags=["Feedback"])


@cbv(router)
class FeedbackCBV:

    """CREATE"""

    @router.post("/feedback", status_code=status.HTTP_201_CREATED, summary="Create feedback (awailable to non-authorized)")
    async def feedback_create(self, entry: FeedbackEntryEditBM) -> FeedbackEntryBM:
        return await FeedbackService.create(entry)

    """ READ """

    @router.get("/feedback/all", summary="Read all feedbacks")
    async def feedback_read_all(self, token: UserTokenBM = Depends(token_required)) -> list[FeedbackEntryBM]:
        return await FeedbackService.read_all(token)

    @router.get("/feedback/{id}", summary="Read specific feedback")
    async def feedback_read_one(self, id: OID, token: UserTokenBM = Depends(token_required)) -> FeedbackEntryBM:
        return await FeedbackService.read_specific(id, token)

    # """ UPDATE """

    # # @router.patch("/tags/{uuid}")
    # # def feedback_update(self, tag: TagBM, token: UserTokenBM = Depends(token_required)):
    # #     return TagsService.update(tag, token)

    """ DELETE """

    @router.delete("/feedback/{id}")
    async def feedback_delete(self, id: OID, token: UserTokenBM = Depends(token_required)):
        await FeedbackService.delete(id, token)

        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content={"result": f"feedback {id} deleted"},
        )
