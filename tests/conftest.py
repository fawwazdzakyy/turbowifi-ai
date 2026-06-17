"""
Test configuration and fixtures.
"""

import pytest
from pathlib import Path

from turbowifi.storage.database import Storage
from turbowifi.storage.queries import Queries


@pytest.fixture
def temp_db(tmp_path: Path) -> Storage:
    db_path = tmp_path / "test.db"
    return Storage(db_path)


@pytest.fixture
def queries(temp_db: Storage) -> Queries:
    return Queries(temp_db)
