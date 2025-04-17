import unittest
from unittest.mock import patch, MagicMock
from app.services import auth


class TestAuthService(unittest.TestCase):

    @patch('app.services.auth.User.get_by_username')
    @patch('app.services.auth.User.check_password')
    def test_authorize_user_success(self, mock_check, mock_get_user):
        mock_get_user.return_value = {'password_hash': 'hashed_password'}
        mock_check.return_value = True
        self.assertTrue(auth.authorize_user('testuser', 'password'))

    @patch('app.services.auth.User.get_by_username')
    def test_authorize_user_oauth_user(self, mock_get_user):
        mock_get_user.return_value = {'password_hash': 'OAuth'}
        self.assertFalse(auth.authorize_user('oauthuser', 'password'))

    @patch('app.services.auth.User.get_by_username', return_value=None)
    def test_authorize_user_user_not_found(self, mock_get_user):
        self.assertFalse(auth.authorize_user('missinguser', 'password'))

    @patch('app.services.auth.User.get_by_username')
    @patch('app.services.auth.User.check_password')
    def test_authorize_user_wrong_password(self, mock_check, mock_get_user):
        mock_get_user.return_value = {'password_hash': 'realhash'}
        mock_check.return_value = False
        self.assertFalse(auth.authorize_user('testuser', 'wrongpass'))

    @patch('app.services.auth.User.get_by_username', return_value=True)
    def test_verify_exist_username_exists(self, mock_username):
        self.assertTrue(auth.verify_exist('user1', 'notchecked@example.com'))

    @patch('app.services.auth.User.get_by_username', return_value=None)
    @patch('app.services.auth.User.get_by_email', return_value=True)
    def test_verify_exist_email_exists(self, mock_email, mock_username):
        self.assertTrue(auth.verify_exist('newuser', 'exists@example.com'))

    @patch('app.services.auth.User.get_by_username', return_value=None)
    @patch('app.services.auth.User.get_by_email', return_value=None)
    def test_verify_exist_user_not_exist(self, mock_email, mock_username):
        self.assertFalse(auth.verify_exist('newuser', 'new@example.com'))

    @patch('app.services.auth.get_google_provider_cfg')
    def test_google_login_redirect_url(self, mock_cfg):
        mock_cfg.return_value = {
            'authorization_endpoint': 'https://accounts.google.com/o/oauth2/auth'
        }

        from flask import Flask
        app = Flask(__name__)

        with app.test_request_context('/login/google'):
            with patch('app.services.auth.redirect') as mock_redirect:
                auth.google_login()
                mock_redirect.assert_called_once()
                redirect_url = mock_redirect.call_args[0][0]
                self.assertIn('client_id', redirect_url)
                self.assertIn('redirect_uri', redirect_url)
                self.assertIn('scope', redirect_url)

    @patch('requests.get')
    def test_get_google_provider_cfg_success(self, mock_get):
        mock_get.return_value.json.return_value = {"authorization_endpoint": "mocked"}
        self.assertEqual(auth.get_google_provider_cfg()['authorization_endpoint'], "mocked")

    @patch('requests.get', side_effect=Exception("connection error"))
    def test_get_google_provider_cfg_failure(self, mock_get):
        self.assertIsNone(auth.get_google_provider_cfg())


if __name__ == '__main__':
    unittest.main()
