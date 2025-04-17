import unittest
from unittest.mock import patch, MagicMock
from app.services import reports


class TestReportService(unittest.TestCase):

    @patch('smtplib.SMTP')
    def test_send_report_email_success(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        success = reports.send_report_email(
            to_email="user@example.com",
            report_type="Performance Report",
            frequency="Weekly",
            report_formats=["PDF", "Excel"],
            additional_notes="Focus on tech sector"
        )

        self.assertTrue(success)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch('smtplib.SMTP', side_effect=Exception("SMTP failure"))
    def test_send_report_email_failure(self, mock_smtp):
        success = reports.send_report_email(
            to_email="fail@example.com",
            report_type="Risk Report",
            frequency="Monthly",
            report_formats=["CSV"],
            additional_notes="N/A"
        )
        self.assertFalse(success)

    @patch('app.services.reports.send_report_email', return_value=True)
    def test_schedule_report_success(self, mock_send):
        result = reports.schedule_report(
            email="user@example.com",
            report_type="Summary",
            frequency="Daily",
            report_formats=["PDF"],
            additional_notes="No additional notes"
        )
        self.assertTrue(result)
        mock_send.assert_called_once()

    @patch('app.services.reports.send_report_email', return_value=False)
    def test_schedule_report_failure(self, mock_send):
        result = reports.schedule_report(
            email="fail@example.com",
            report_type="Summary",
            frequency="Daily",
            report_formats=["PDF"],
            additional_notes=""
        )
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
