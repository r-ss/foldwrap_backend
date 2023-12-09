# -*- coding: utf-8 -*-
# -----------------------------------
# @CreateTime   : 2020/7/25 0:27
# @Author       : Mark Shawn
# @Email        : shawninjuly@gmail.com
# ------------------------------------
import json
from datetime import date, datetime
from enum import Enum
from typing import Dict, List, Union
from uuid import UUID

from bson import ObjectId
from pydantic import BaseModel


def mongo_json_encoder(record: Union[Dict, List, BaseModel]):
    """
    This is a json_encoder designed specially for dump mongodb records.
    It can deal with both record_item and record_list type queried from mongodb.
    You can extend the encoder ability in the recursive function `convert_type`.
    I just covered the following datatype: datetime, date, UUID, ObjectID.
    Contact me if any further support needs.
    Attention: it will change the raw record, so copy it before operating this function if necessary.

    Parameters
    ----------
    **record**: a dict or a list, like the queried documents from mongodb.

    Returns
    -------
    json formatted data.
    """

    def convert_type(data):
        # if isinstance(data, (datetime, date)):
        #     # ISO format: data.isoformat()
        #     return data
        if isinstance(data, datetime):
            # ISO format: data.isoformat()
            return data
        if isinstance(data, date):
            # ISO format: data.isoformat()
            return str(data)
        # elif isinstance(data, (UUID, ObjectId)):
        #     return str(data)
        elif isinstance(data, (ObjectId)):
            return ObjectId(data)
        elif isinstance(data, (UUID)):
            return str(data)
        elif isinstance(data, list):
            return list(map(convert_type, data))
        elif isinstance(data, dict):
            return mongo_json_encoder(data)
        elif isinstance(data, Enum):
            return str(data.value)
        try:
            json.dumps(data)
            return data
        except TypeError:
            raise TypeError(
                {
                    "error_msg": "custom 暂不支持此类型序列化",
                    "key": key,
                    "value": value,
                    "type": type(value),
                }
            )

    # add support for BaseModel
    if isinstance(record, BaseModel):
        return mongo_json_encoder(record.dict(by_alias=True))
    elif isinstance(record, dict):
        for key, value in record.items():
            record[key] = convert_type(value)
        return record
    else:
        return list(map(mongo_json_encoder, record))
