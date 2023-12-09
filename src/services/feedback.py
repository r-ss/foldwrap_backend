from typing import List

from models.feedback import FeedbackEntryBM, FeedbackEntryEditBM
from models.user import UserTokenBM

from services.users.auth import sudo_only
from services.misc.utils import send_bot_message

from dao.oid import OID
from dao.dao_feedback import FeedbackDAOLayer

FeedbackDAO = FeedbackDAOLayer()


class FeedbackService:

    """CREATE SERVICE"""

    async def create(entry: FeedbackEntryEditBM) -> FeedbackEntryBM:
        """Create feedback entry and return it"""

        # feedback = FeedbackDAO.get_note_owner(uuid=note_uuid)

        feedback = await FeedbackDAO.create(FeedbackEntryBM.parse_obj({"theme": entry.theme, "email": entry.email, "name": entry.name, "message": entry.message}))

        msg = f"""💁 New feedback
{ str(feedback.theme) }
{feedback.email}
Name: {feedback.name}
--- message: ---
{feedback.message}
"""
        send_bot_message(msg)

        return feedback

    """ READ SERVICE """

    async def read_specific(id: OID, token: UserTokenBM) -> FeedbackEntryBM:
        """Get specific feedback item"""
        sudo_only(token)
        return await FeedbackDAO.read(id=id)

    async def read_all(token: UserTokenBM) -> List[FeedbackEntryBM]:
        """Get all feedback items"""
        sudo_only(token)
        return await FeedbackDAO.read_all()

    """ UPDATE SERVICE """
    # def update(input_tag: TagBM, token: UserTokenBM) -> TagBM:
    #     """Method to change tag name"""

    #     # Get all user tags to check ownership
    #     # TODO - consider refactor
    #     usertags = TagsService.read_all_for_user(token.uuid, token)
    #     found = False
    #     for tag in usertags:
    #         if tag.uuid == input_tag.uuid:
    #             found = True
    #             break

    #     if not found:
    #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized. Tag not found for user")

    #     return TagDAO.update_fields(uuid=tag.uuid, fields={"name": input_tag.name, "color": str(input_tag.color)})

    """ DELETE SERVICE """

    async def delete(id: OID, token: UserTokenBM) -> None:
        """Delete Feedback entry from database"""
        sudo_only(token)
        await FeedbackDAO.delete(id=id)
