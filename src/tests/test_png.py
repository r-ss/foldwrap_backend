import pytest
import pathlib
import hashlib

from config import config

from services.misc.filesystem import FileSystemUtils as fs

from services.misc.png_optimizer import PNGOptimizer


lambo_path = pathlib.Path(config.TESTING_ASSETS_PATH).joinpath("lambo.png")


@pytest.mark.anyio
async def test_png():
    before_size = fs.get_filesize(lambo_path, kb=True)
    out_path = pathlib.Path(config.DATA_DIR_TEMP).joinpath("lambo_opt.png")
    optimizer = PNGOptimizer()

    print("Before:", before_size)
    optimizer.optimize_PNG(lambo_path, out_path)
    after_size = fs.get_filesize(out_path, kb=True)
    print("After:", after_size)

    assert after_size < before_size
