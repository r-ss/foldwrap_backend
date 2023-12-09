# import re
from pydantic import BaseModel


class BannerExportBM(BaseModel):
    title: str
    size: str
    nodes_data: dict
    html: str
    css: str
    # data: str
    figma_key: str | None = None
    headinjection: str | None = None  # used to link Google Fonts...
