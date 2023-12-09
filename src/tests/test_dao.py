import pytest

from dao.dao_user import UserDAOLayer
from dao.maintenance.dao_test import DAOTestLayer
from models.maintenance.test import BMTest

DAOTest = DAOTestLayer()
UserDAO = UserDAOLayer()


@pytest.mark.anyio
async def test_dao_crud():
    """Set of checks to be sure our Data Access Layer (DAO)
    works properly.
    Needs a special Pydantic's BaseModel BMTest
    and DAOTestLayer which is subclass of BasicDAOLayer
    """

    """ COUNT """

    all = await DAOTest.read_all()
    count = len(all)

    """ CREATE """

    # db_user = await UserDAO.get_by_email(email=f"alice@{config.DOMAIN}")
    # print(db_user)

    # item = BMTest(content="content body", child=db_user.id)
    item = BMTest(content="content body")
    result = await DAOTest.create(item)

    assert result.id == item.id
    assert result.content == item.content
    # assert result.created.replace(microsecond=0) == item.created.replace(microsecond=0)

    assert isinstance(result.id, type(item.id))
    assert isinstance(result.content, type(item.content))
    # assert type(result.created) == type(item.created)

    """ READ """

    read = await DAOTest.read(item.id)
    # read.child = await UserDAO.read(item.child, removehash=True)

    # print(read.json())

    assert read.id == item.id
    assert read.content == item.content
    # assert read.created.replace(microsecond=0) == item.created.replace(microsecond=0)

    assert isinstance(read.id, type(item.id))
    assert isinstance(read.content, type(item.content))
    # assert type(read.created) == type(item.created)

    all = await DAOTest.read_all()
    assert isinstance(all, type([]))
    assert isinstance(all[0], BMTest)
    assert len(all) == count + 1

    """ UPDATE """

    edit = item.copy()
    edit.content = "updated content"

    updated = await DAOTest.update(edit)

    assert updated.id == item.id
    assert updated.content == edit.content
    # assert updated.created.replace(microsecond=0) == item.created.replace(microsecond=0)

    assert isinstance(updated.id, type(item.id))
    assert isinstance(updated.content, type(item.content))
    # assert type(updated.created) == type(item.created)

    """ DELETE """

    delete_result = await DAOTest.delete(item.id)
    assert delete_result is True

    """ COUNT AGAIN """

    all = await DAOTest.read_all()
    assert len(all) == count
