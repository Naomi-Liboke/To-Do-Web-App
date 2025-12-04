from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock
import sys


class ManagePyTests(SimpleTestCase):
    @patch('django.core.management.execute_from_command_line')
    @patch('os.environ.setdefault')
    def test_main_sets_env_and_executes(self, mock_setdefault, mock_execute):
        # Simulate command-line args
        test_args = ['manage.py', 'check']
        with patch.object(sys, 'argv', test_args):
            from manage import main
            main()

        # Check environment variable was set
        mock_setdefault.assert_called_once_with('DJANGO_SETTINGS_MODULE', 'blog_project.settings')

        # Check execute_from_command_line was called with sys.argv
        mock_execute.assert_called_once_with(test_args)

    def test_main_import_error(self):
        with patch.dict('sys.modules', {'django.core.management': None}):
            with self.assertRaises(ImportError) as context:
                from manage import main
                main()
            self.assertIn("Couldn't import Django", str(context.exception))
