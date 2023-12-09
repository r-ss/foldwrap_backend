import timeit

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from config import config
from dao.mongo_json_encoder import mongo_json_encoder

# from dao.ress_redis import RessRedisAbstraction
from models.meta import MetaBM

# redis = RessRedisAbstraction()

# redis_enabled = False
# log("checking redis...", level="debug")
# if not redis.ping():
#     log("redis ping failed, setting to redis_enabled false", level="warning")
#     redis_enabled = False

from log import log


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


async def database_healthcheck():
    """Separate function (not includein in the DAO class) to check DB health"""
    client = AsyncIOMotorClient(
        host=config.DBHOST,
        serverSelectionTimeoutMS=1500,
    )
    try:
        response = await client.server_info()
        return response["version"]
    except Exception as e:
        log(f"Error while checking MongoDB health: {str(e)}", level="error")
        return False


class BasicDAOLayer:
    """Some general methods to basic operations with database

    Operates with abstract "Object" implying Pydantic models
    This class must be inherited by more specific objects like Note, which provide context
    """

    def __init__(self):
        # client = AsyncIOMotorClient(host=config.DBHOST)

        client = AsyncIOMotorClient(
            host=config.DBHOST,
            # timeoutMS=2500,
            # socketTimeoutMS=2500,
            # connectTimeoutMS=2500,
            serverSelectionTimeoutMS=10000,
        )

        if config.PRODUCTION:
            self.db = client.production_db  # PRODUCTION DB
        else:
            self.db = client.test_db  # TEST DB

        self.collection_name = "default_test"  # collection mane must be overwritten dy subclass
        self.model = None  # Pydantic model must be put here by subclass
        self.collection = None  # Overwrite in subclass

    async def create(self, item):
        """Create one item from pydntic BaseModel object provided"""
        encoded = mongo_json_encoder(item.copy())
        if "meta" in encoded:
            encoded.pop("meta")  # remove meta field to prevent writing it into DB

        try:
            new_entry = await self.collection.insert_one(encoded)
        except DuplicateKeyError:
            raise HTTPException(status_code=409, detail="Can't add entry for BD (DuplicateKeyError)")

        # saving to DB
        created_entry = await self.collection.find_one({"_id": new_entry.inserted_id})
        obj = self.model.parse_obj(created_entry)

        # saving to Redis
        # if redis_enabled and created_entry["_id"]:
        #     rkey = f"{self.collection_name}-{created_entry['_id']}"
        #     redis.set(rkey, obj.json())

        return obj

    async def read_all(self, limit=1000):
        """Read all items and return as a list of Pydantic objects"""
        bin = []
        for row in await self.collection.find().to_list(limit):
            bin.append(self.model.parse_obj(row))
        return bin

    async def read(self, id: str):
        """Read and return one item from DB as Pydantic object"""

        benchmark_start = timeit.default_timer()

        # if redis_enabled:
        #     rkey = f"{self.collection_name}-{id}"
        #     raw = redis.get(rkey)
        #     if raw:
        #         print("returning from redis")
        #         item = self.model.parse_raw(raw)
        #         benchmark = f"{timeit.default_timer() - benchmark_start:.4f}s"
        #         del benchmark_start
        #         if hasattr(item, "meta"):
        #             item.meta = MetaBM(datasource="redis", benchmark=benchmark)
        #         return item

        # print("returning from db")
        if (db_entry := await self.collection.find_one({"_id": ObjectId(id)})) is not None:
            item = self.model.parse_obj(db_entry)

            # caching to Redis
            # if redis_enabled:
            #     rkey = f"{self.collection_name}-{item.id}"
            #     redis.set(rkey, item.json())

            benchmark = f"{timeit.default_timer() - benchmark_start:.4f}s"
            del benchmark_start
            if hasattr(item, "meta"):
                item.meta = MetaBM(datasource="database", benchmark=benchmark)
            return item
        raise HTTPException(status_code=404, detail=f"Item {id} not found")

    async def update(self, item, removehash=True):
        """Update in DB and return one item as Pydantic object"""
        # as_dict = {k: v for k, v in item.dict().items() if v is not None and k != "id" and k != "userhash"}
        if removehash:
            as_dict = {k: v for k, v in item.dict().items() if k != "id" and k != "userhash"}
        else:
            as_dict = {k: v for k, v in item.dict().items() if k != "id"}
        # ^^^^^ eliminating empty values and also ID to prevent arrearing an "id" field in mongo db

        """ PAY ATTENTION TO NONE VALUES """

        encoded = mongo_json_encoder(as_dict.copy())

        if "meta" in as_dict:
            encoded.pop("meta")  # remove meta field to prevent writing it into DB

        update_result = await self.collection.update_one({"_id": ObjectId(item.id)}, {"$set": encoded})
        if update_result.modified_count == 1:
            if (updated_item := await self.collection.find_one({"_id": ObjectId(item.id)})) is not None:
                obj = self.model.parse_obj(updated_item)

                # saving update to Redis
                # if redis_enabled and updated_item["_id"]:
                #     rkey = f"{self.collection_name}-{updated_item['_id']}"
                #     redis.set(rkey, obj.json())
                return obj

        # in case item not actually updated
        if (existing_result := await self.collection.find_one({"_id": ObjectId(item.id)})) is not None:
            return self.model.parse_obj(existing_result)

        raise HTTPException(status_code=404, detail=f"Error in updating. Item {item.id}, is it existed in DB?")

    async def delete(self, id: str):
        """Delete one item from DB and return True"""
        delete_result = await self.collection.delete_one({"_id": ObjectId(id)})

        if delete_result.deleted_count == 1:
            # also deleting from Redis
            # if redis_enabled:
            #     rkey = f"{self.collection_name}-{id}"
            #     redis.delete(rkey)

            return True

        raise HTTPException(status_code=404, detail=f"Item {id} not found")
