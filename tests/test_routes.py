import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from flask import session


class TestApiRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_index_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    @patch('app.api.routes.authorize_user', return_value=True)
    @patch('app.api.routes.User.get_by_username')
    def test_login_success(self, mock_get_user, mock_auth):
        mock_get_user.return_value = {'id': 1}
        response = self.app.post('/login', data={'username': 'test', 'password': 'pass'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    @patch('app.api.routes.authorize_user', return_value=False)
    def test_login_failure(self, mock_auth):
        response = self.app.post('/login', data={'username': 'baduser', 'password': 'badpass'})
        self.assertIn(b'Username not exist or password not match', response.data)

    @patch('app.api.routes.verify_exist', return_value=True)
    def test_register_existing_user(self, mock_verify):
        response = self.app.post('/signup', data={
            'username': 'taken',
            'email': 'test@example.com',
            'password': 'pass',
            'firstname': 'Test',
            'lastname': 'User'
        })
        self.assertIn(b'already exists', response.data)

    @patch('app.api.routes.verify_exist', return_value=False)
    @patch('app.api.routes.User.save')
    def test_register_new_user(self, mock_save, mock_verify):
        response = self.app.post('/signup', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'pass',
            'firstname': 'New',
            'lastname': 'User'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', response.data)

    @patch('app.api.routes.get_recent_stock_news')
    def test_news_page(self, mock_news):
        mock_news.return_value = [{'title': 'Fake News'}]
        response = self.app.get('/news')
        self.assertEqual(response.status_code, 200)

    @patch('app.api.routes.get_time_series_for_stock')
    def test_get_stock_data_api(self, mock_data):
        mock_data.return_value = {'data': 'mocked'}
        response = self.app.get('/api/stock/AAPL')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'mocked', response.data)

    @patch('app.api.routes.schedule_report', return_value=True)
    def test_report_submission_success(self, mock_schedule):
        response = self.app.post('/report', data={
            'email': 'user@example.com',
            'report_type': 'Performance Report',
            'frequency': 'Weekly',
            'pdf': 'on',
            'notes': 'none'
        }, follow_redirects=True)
        self.assertIn(b'Report scheduled', response.data)

    def test_logout(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1

        response = self.app.get('/logout', follow_redirects=True)

        with self.app.session_transaction() as sess:
            self.assertNotIn('user_id', sess)

        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
