from dao.dao import BasicDAOLayer
from models.maintenance.test import BMTest


class DAOTestLayer(BasicDAOLayer):
    def __init__(self):
        super().__init__()
        self.collection_name = "test_collection"
        self.model = BMTest
        self.collection = self.db[self.collection_name]
