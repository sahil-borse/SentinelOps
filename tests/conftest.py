import pytest

from sentinelops.db import connect
from sentinelops.repositories import repositories


@pytest.fixture()
def conn(tmp_path):
    connection = connect(tmp_path / "test.db")
    yield connection
    connection.close()


@pytest.fixture()
def repo(conn):
    return repositories(conn)
