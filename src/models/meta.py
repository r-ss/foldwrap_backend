from pydantic import BaseModel


class MetaBM(BaseModel):
    datasource: str
    benchmark: str
