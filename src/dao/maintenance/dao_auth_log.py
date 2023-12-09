from dao.dao import BasicDAOLayer
from models.maintenance.auth_log import AuthLogEntryBM


class AuthLogDAOLayer(BasicDAOLayer):
    def __init__(self):
        super().__init__()
        self.collection_name = "auth_log"
        self.model = AuthLogEntryBM
        self.collection = self.db[self.collection_name]
