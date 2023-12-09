# Solution about mongodb ID fields with FastAPI and Pydantic:
# Taken from here: https://github.com/tiangolo/fastapi/issues/1515

# Another article: https://www.mongodb.com/developer/languages/python/python-quickstart-fastapi/#wrapping-up

# from typing import Annotated, Any, Callable

from bson import ObjectId
from bson.errors import InvalidId
from pydantic_core import core_schema

# from pydantic.json_schema import JsonSchemaValue


class OID(str):
    """Substitution of ObjectId for Pydantic models"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")

    # @classmethod
    # def __get_pydantic_json_schema__(cls, field_schema):
    #     field_schema.update(type="string")

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, _handler) -> core_schema.CoreSchema:
        assert source_type is OID
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )
