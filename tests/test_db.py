from src.db import test_connection


def test_database_connection():
    result = test_connection()

    assert result == 1