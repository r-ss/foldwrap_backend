from pathlib import Path
from config import config

from models.export import BannerExportBM
from services.foldwrap_banner import FoldWrapBanner



class ExportService:
    async def export_banner(banner_data: BannerExportBM):
        """Export FoldWrap banner and return link to ZIP bundle"""

        banner = FoldWrapBanner(banner_data)

        export_path = Path(config.DATA_DIR_TEMP).joinpath("export")
        if banner.figma_key:
            export_path = export_path.joinpath(banner.figma_key)

        result = banner.exportAsHTML(export_path)

        return result
