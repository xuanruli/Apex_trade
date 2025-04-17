import unittest
from unittest.mock import patch, MagicMock
from app.services import email


class TestEmailService(unittest.TestCase):

    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        email.send_email("Test Subject", "Test Body", "test@example.com")

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('smtplib.SMTP', side_effect=Exception("Connection failed"))
    def test_send_email_failure(self, mock_smtp):
        # Just make sure it doesn't raise, since we catch exceptions inside
        email.send_email("Test", "Body", "fail@example.com")

    @patch('app.services.email.send_email')
    def test_send_report_with_holdings_and_analysis(self, mock_send_email):
        holdings = {"AAPL": "10 shares @ $150", "TSLA": "5 shares @ $700"}
        analysis = {"Total Value": "$5,500", "Risk": "Medium"}
        content = "This is your performance report."

        email.send_report("user@example.com", content, portfolio_holdings=holdings, analysis=analysis)

        called_subject = mock_send_email.call_args[0][0]
        called_body = mock_send_email.call_args[0][1]

        self.assertIn("Your Portfolio Holdings", called_body)
        self.assertIn("Your Portfolio Analysis", called_body)
        self.assertIn("AAPL: 10 shares", called_body)
        self.assertIn("Risk: Medium", called_body)
        self.assertEqual(called_subject, "Your Apex Trades Report")

    @patch('app.services.email.send_email')
    def test_send_password_reset(self, mock_send_email):
        email.send_password_reset("user@example.com", "123456-token")
        subject, body, to = mock_send_email.call_args[0]
        self.assertEqual(subject, "Password Reset Request")
        self.assertIn("123456-token", body)
        self.assertEqual(to, "user@example.com")


if __name__ == '__main__':
    unittest.main()
