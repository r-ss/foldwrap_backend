from fastapi import status
from fastapi_restful.cbv import cbv
from fastapi_restful.inferring_router import InferringRouter

from models.export import BannerExportBM

from services.export import ExportService

router = InferringRouter(tags=["Banner export"])


@cbv(router)
class ExportCBV:

    """CREATE"""

    @router.post("/export", status_code=status.HTTP_201_CREATED, summary="Export FoldWrap banner and get back link to ZIP bundle")
    async def export_banner(self, banner_data: BannerExportBM):
        result = await ExportService.export_banner(banner_data)

        return result
