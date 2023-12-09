from dao.dao import BasicDAOLayer
from models.feedback import FeedbackEntryBM


class FeedbackDAOLayer(BasicDAOLayer):
    def __init__(self):
        super().__init__()
        self.collection_name = "feedback"
        self.model = FeedbackEntryBM
        self.collection = self.db[self.collection_name]
