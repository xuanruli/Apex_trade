import unittest
from unittest.mock import patch
from app.models.user import User
from werkzeug.security import check_password_hash


class TestUser(unittest.TestCase):

    @patch('app.models.user.execute_update')
    @patch('app.models.user.execute_query')
    def test_save_new_user(self, mock_query, mock_update):
        mock_query.return_value = [{'id': 1}]
        user = User("testuser", "test@example.com", "Test", "User", "securepass")
        user.save()
        self.assertEqual(user._id, 1)
        mock_update.assert_called_once()
        self.assertTrue(check_password_hash(user._password_hash, "securepass"))

    @patch('app.models.user.execute_update')
    def test_save_existing_user(self, mock_update):
        user = User("testuser", "test@example.com", "Test", "User", "securepass")
        user._id = 2  # Simulate existing user
        user.save()
        mock_update.assert_called_once()

    @patch('app.models.user.execute_query')
    def test_get_by_username_found(self, mock_query):
        mock_query.return_value = [{
            'id': 1, 'username': 'testuser', 'email': 'test@example.com',
            'firstname': 'Test', 'lastname': 'User', 'password_hash': 'hashedpass'
        }]
        result = User.get_by_username("testuser")
        self.assertEqual(result['username'], 'testuser')

    @patch('app.models.user.execute_query')
    def test_get_by_username_not_found(self, mock_query):
        mock_query.return_value = []
        result = User.get_by_username("ghostuser")
        self.assertIsNone(result)

    @patch('app.models.user.execute_query')
    def test_get_by_email_found(self, mock_query):
        mock_query.return_value = [{
            'id': 1, 'username': 'testuser', 'email': 'test@example.com',
            'firstname': 'Test', 'lastname': 'User', 'password_hash': 'hashedpass'
        }]
        result = User.get_by_email("test@example.com")
        self.assertEqual(result['email'], 'test@example.com')

    @patch('app.models.user.execute_query')
    def test_get_by_email_not_found(self, mock_query):
        mock_query.return_value = []
        result = User.get_by_email("missing@example.com")
        self.assertIsNone(result)

    @patch("app.models.user.execute_update")
    def test_change_password(self, mock_update):
        user = User("testuser", "test@example.com", "Test", "User", "oldpass")
        user._id = 1

        user.change_password(1, "newpass123")

        mock_update.assert_called_once()
        _, params = mock_update.call_args[0]  # (query, params)
        new_hash, uid = params
        self.assertEqual(uid, 1)
        self.assertTrue(check_password_hash(new_hash, "newpass123"))

    @patch('app.models.user.execute_query')
    def test_check_password_correct(self, mock_query):
        from werkzeug.security import generate_password_hash
        password = "mypass"
        mock_query.return_value = [{
            'username': 'testuser',
            'email': 'test@example.com',
            'firstname': 'Test',
            'lastname': 'User',
            'password_hash': generate_password_hash(password)
        }]
        result = User.check_password("testuser", "mypass")
        self.assertTrue(result)

    @patch('app.models.user.execute_query')
    def test_check_password_incorrect(self, mock_query):
        from werkzeug.security import generate_password_hash
        mock_query.return_value = [{
            'username': 'testuser',
            'email': 'test@example.com',
            'firstname': 'Test',
            'lastname': 'User',
            'password_hash': generate_password_hash("rightpass")
        }]
        result = User.check_password("testuser", "wrongpass")
        self.assertFalse(result)

    @patch('app.models.user.execute_query')
    def test_check_password_user_not_found(self, mock_query):
        mock_query.return_value = []
        result = User.check_password("ghost", "any")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
