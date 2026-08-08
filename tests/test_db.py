from src.db import check_connection


def test_database_connection():
    result = check_connection()

    assert result == 1