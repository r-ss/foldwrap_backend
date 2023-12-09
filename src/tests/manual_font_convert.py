import pytest
from pathlib import Path
from config import config

# from tests.testutils import get


from services.misc.fonts import FontTool


@pytest.mark.anyio
async def test_foldwrap_banner_a():
    names = ["OfficinaSerifBookC.otf", "DaggerC.otf", "Secretary.ttf"]

    # for name in names:

    #     input =  Path(config.TESTING_ASSETS_PATH).joinpath(f"fonts/{name}")
    #     output = Path(config.DATA_DIR_TEMP).joinpath(f"{name}.woff")

    #     FontTool.convert_to_woff(input, output)

    input = Path(config.TESTING_ASSETS_PATH).joinpath(f"fonts/{names[0]}")
    output = Path(config.DATA_DIR_TEMP).joinpath(f"{names[0]}.woff")

    FontTool.convert_to_woff(input, output)
