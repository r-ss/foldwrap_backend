import random
import string

import pytest

from log import log


@pytest.mark.anyio
async def test_logging():
    def test_logging():
        for _ in range(10):
            # Generate a random string
            random_string = "".join(random.choice(string.ascii_letters) for _ in range(10))

            # Log the random string with a random log level
            log_levels = ["debug", "info", "warning", "error", "critical"]
            random_level = random.choice(log_levels)

            log(f"Random string: {random_string}", level=random_level)

    test_logging()
