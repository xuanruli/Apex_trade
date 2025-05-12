import unittest
from unittest.mock import patch, MagicMock
from app.db.schema import setup_database


class TestSchema(unittest.TestCase):
    @patch("app.db.schema.mysql.connector.connect")
    def test_setup_database_executes_all_commands(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        setup_database()

        self.assertGreaterEqual(mock_cursor.execute.call_count, 7)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
