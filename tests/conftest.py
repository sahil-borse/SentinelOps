import pytest

from sentinelops.db import connect
from sentinelops.repositories import repositories


@pytest.fixture()
def conn():
    """In memory, because every repository write commits.

    A full S1 cycle writes ~2000 rows and therefore ~2000 commits; against a
    file on disk that is thousands of fsyncs and turns the suite from seconds
    into minutes. Durability is not what these tests are checking.
    """
    connection = connect(":memory:")
    yield connection
    connection.close()


@pytest.fixture()
def repo(conn):
    return repositories(conn)
