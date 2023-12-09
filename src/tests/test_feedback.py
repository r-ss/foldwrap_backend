import pytest
from tests.testutils import delete, get, post, postForm

from config import config


@pytest.mark.anyio
async def test_feedback_crud(client, jesus):
    testdata = {"theme": "test", "email": "carly@foldwrap.com", "name": "Carly Rae Jepsen", "message": "So Call Me Maybe"}

    """ COUNT """
    status_code, result = await get(client, "/feedback/all", auth=jesus.token)
    feedbacks_count = len(result)
    assert status_code == 200

    """ CREATE """

    status_code, result = await post(client, f"/feedback", testdata)
    created_feedback = result
    assert status_code == 201  # HTTP_201_CREATED
    assert created_feedback["name"] == testdata["name"]
    assert created_feedback["message"] == testdata["message"]

    """ READ """

    status_code, result = await get(client, "/feedback/%s" % created_feedback["_id"])
    assert status_code == 401

    status_code, result = await get(client, "/feedback/%s" % created_feedback["_id"], auth=jesus.token)
    assert status_code == 200
    assert result["message"] == testdata["message"]

    status_code, result = await get(client, "/feedback/all", auth=jesus.token)
    assert status_code == 200

    """ DELETE """

    status_code, result = await delete(client, "/feedback/%s" % created_feedback["_id"], auth=jesus.token)
    assert status_code == 204

    """ COUNT AGAIN """

    status_code, result = await get(client, "/feedback/all", auth=jesus.token)
    assert feedbacks_count == len(result)
