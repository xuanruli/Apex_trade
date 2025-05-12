import unittest
from unittest.mock import patch, MagicMock
from app import create_app


class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_index_page(self):
        rv = self.app.get("/")
        self.assertEqual(rv.status_code, 200)

    @patch("app.api.routes.Portfolio.get_by_user_id")
    @patch("app.api.routes.Portfolio.check_portfolio", return_value=False)
    @patch("app.api.routes.User.get_by_username")
    @patch("app.api.routes.authorize_user", return_value=True)
    def test_login_success(
        self,
        mock_auth,
        mock_get_user,
        mock_check_portfolio,
        mock_get_portfolio,
    ):
        mock_get_user.return_value = {"id": 1, "firstname": "T", "lastname": "U"}
        mock_get_portfolio.return_value = MagicMock()

        rv = self.app.post(
            "/login",
            data={"username": "test", "password": "pass"},
            follow_redirects=True,
        )
        self.assertEqual(rv.status_code, 200)

    @patch("app.api.routes.authorize_user", return_value=False)
    def test_login_failure(self, _):
        rv = self.app.post(
            "/login", data={"username": "bad", "password": "badpass"}
        )
        self.assertIn(b"Username not exist or password not match", rv.data)

    @patch("app.api.routes.verify_exist", return_value=True)
    def test_register_existing_user(self, _):
        rv = self.app.post(
            "/signup",
            data={
                "username": "taken",
                "email": "e@x.com",
                "password": "p",
                "firstname": "F",
                "lastname": "L",
            },
        )
        self.assertIn(b"already exists", rv.data)

    @patch("app.api.routes.User.save")
    @patch("app.api.routes.verify_exist", return_value=False)
    def test_register_new_user(self, _verify, _save):
        rv = self.app.post(
            "/signup",
            data={
                "username": "new",
                "email": "n@x.com",
                "password": "p",
                "firstname": "N",
                "lastname": "U",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Registration successful", rv.data)

    @patch("app.api.routes.get_recent_stock_news", return_value=[{"title": "Fake"}])
    def test_news_page(self, _):
        rv = self.app.get("/news")
        self.assertEqual(rv.status_code, 200)

    @patch("app.api.routes.render_template", return_value="OK")
    @patch(
        "app.api.routes.load_asset_page",
        return_value=(
            "AAPL",
            "candle",
            "line",
            "bar",
            ["Title"],
            ["URL"],
            "2020-01-01",
            "2020-12-31",
        ),
    )
    def test_asset_page(self, *_):
        rv = self.app.get("/asset")
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b"OK", rv.data)

    @patch("app.api.routes.schedule_report", return_value=True)
    def test_report_submission_success(self, _):
        rv = self.app.post(
            "/report",
            data={
                "email": "u@x.com",
                "report_type": "Performance Report",
                "frequency": "Weekly",
                "pdf": "on",
                "notes": "n",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Report scheduled", rv.data)

    def test_logout(self):
        with self.app.session_transaction() as s:
            s["id"] = 1
        rv = self.app.get("/logout", follow_redirects=True)
        with self.app.session_transaction() as s:
            self.assertNotIn("id", s)
        self.assertEqual(rv.status_code, 200)


if __name__ == "__main__":
    unittest.main()
