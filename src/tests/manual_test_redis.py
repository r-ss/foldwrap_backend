import pytest
import random

from dao.ress_redis import RessRedisAbstraction


def generate_code():
    return str(random.randint(100000, 999999))


@pytest.mark.anyio
async def test_redis():
    redis = RessRedisAbstraction()

    assert redis.ping() is True

    code = generate_code()
    value = generate_code()

    redis.set(f"activation-code:{code}", value)

    assert redis.get(f"activation-code:{code}") == value
    assert redis.get(f"activation-code:{ generate_code() }not-exists") is None
