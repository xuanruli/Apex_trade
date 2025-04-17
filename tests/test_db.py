import unittest
from unittest.mock import patch, MagicMock
import sqlite3
from app.db import initialize_database, execute_query, execute_update


class TestDBFunctions(unittest.TestCase):

    @patch('app.db.setup_database')
    @patch('app.db.process_all_stocks')
    def test_initialize_database(self, mock_process, mock_setup):
        initialize_database()
        mock_setup.assert_called_once()
        mock_process.assert_called_once()

    @patch('sqlite3.connect')
    def test_execute_query_returns_dicts(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.description = [('id',), ('name',)]
        mock_cursor.fetchall.return_value = [(1, 'Apple'), (2, 'Microsoft')]

        result = execute_query("SELECT * FROM stocks")

        self.assertEqual(result, [{'id': 1, 'name': 'Apple'}, {'id': 2, 'name': 'Microsoft'}])
        mock_conn.close.assert_called_once()

    @patch('sqlite3.connect')
    def test_execute_update_success(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.rowcount = 1

        rowcount = execute_update("UPDATE users SET name=? WHERE id=?", ("Test", 1))
        self.assertEqual(rowcount, 1)
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
