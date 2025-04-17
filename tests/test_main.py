import unittest
from unittest.mock import patch
from io import StringIO
import sys

class TestMainFunction(unittest.TestCase):

    @patch('app.db.setup_database')
    @patch('app.db.process_all_stocks')
    def test_main(self, mock_process_all_stocks, mock_setup_database):
        from app.db import initialize_database

        # Import the function after patching to ensure the mocks are used
        
        # Capture print output
        captured_output = StringIO()
        sys.stdout = captured_output

        # Call main
        initialize_database()

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Assertions
        mock_setup_database.assert_called_once()
        mock_process_all_stocks.assert_called_once()
        self.assertIn("Database Init Complete", captured_output.getvalue())

if __name__ == '__main__':
    unittest.main()
