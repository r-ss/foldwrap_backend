from bson import ObjectId

from dao.dao import BasicDAOLayer
from dao.oid import OID
from models.figma_file import FigmaFileBM


class FigmaFileDAOLayer(BasicDAOLayer):
    def __init__(self):
        super().__init__()
        self.collection_name = "figma_file"
        self.model = FigmaFileBM
        self.collection = self.db[self.collection_name]

    async def read_all_for_user(self, user_id: OID, limit=100):
        bin = []
        for row in await self.collection.find({"owner": ObjectId(user_id)}).sort("created", -1).to_list(limit):
            bin.append(self.model.parse_obj(row))

        return bin
