from django.test import TestCase, override_settings
from django.core import mail
from unittest.mock import patch, mock_open, Mock
import os
from to_do_app.utils import email


class SendHtmlEmailWithLogoTests(TestCase):
    @override_settings(
        DEFAULT_FROM_EMAIL="noreply@example.com",
        BASE_DIR="C:/fakebase"  # fake path for logo
    )
    @patch("to_do_app.utils.email.EmailMultiAlternatives.attach")
    @patch("to_do_app.utils.email.MIMEImage")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fakeimagebytes")
    def test_send_html_email_with_logo(self, mock_file, mock_mimeimage, mock_attach):
        # Patch render_to_string to return simple HTML
        with patch("to_do_app.utils.email.render_to_string", return_value="<p>Hello tester</p>"):
            # Ensure MIMEImage returns a mock object with headers so code can call add_header
            mock_mimeimage.return_value = Mock()
            # Patch the attach method so Django doesn't validate the mock
            mock_attach.return_value = None

            # Call the function
            email.send_html_email_with_logo(
                subject="Test Subject",
                template_name="fake_template.html",
                context={"user": "tester"},
                recipient="tester@example.com"
            )

        # Verify email was sent
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.subject, "Test Subject")
        self.assertEqual(sent.from_email, "noreply@example.com")
        self.assertEqual(sent.to, ["tester@example.com"])
        # HTML alternative should be attached
        self.assertIn("<p>Hello tester</p>", sent.alternatives[0][0])
        self.assertEqual(sent.alternatives[0][1], "text/html")

        # Verify logo file was opened
        expected_path = os.path.join("C:/fakebase", 'to_do_app', 'static', 'to_do_app', 'images', 'focusflow-logo.png')
        mock_file.assert_called_once_with(expected_path, "rb")

        # MIMEImage should have been called with the raw bytes
        mock_mimeimage.assert_called()
        # attach should have been used to attach the logo
        mock_attach.assert_called()

    @override_settings(DEFAULT_FROM_EMAIL="noreply@example.com", BASE_DIR="C:/fakebase")
    @patch("to_do_app.utils.email.EmailMultiAlternatives.attach")
    @patch("to_do_app.utils.email.MIMEImage")
    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_send_html_email_with_logo_missing_file(self, mock_file, mock_mimeimage, mock_attach):
        with patch("to_do_app.utils.email.render_to_string", return_value="<p>Hello tester</p>"):
            # Even if logo file is missing, function should raise FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                email.send_html_email_with_logo(
                    subject="Test Subject",
                    template_name="fake_template.html",
                    context={"user": "tester"},
                    recipient="tester@example.com"
                )
