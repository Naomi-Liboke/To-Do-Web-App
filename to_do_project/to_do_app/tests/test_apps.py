from django.test import TestCase
from django.apps import apps
from to_do_app.apps import ToDoAppConfig


class ToDoAppConfigTests(TestCase):
    def test_app_config_name(self):
        # Use the app registry to get the loaded AppConfig instance
        config = apps.get_app_config('to_do_app')
        self.assertEqual(config.name, 'to_do_app')

    def test_default_auto_field(self):
        config = apps.get_app_config('to_do_app')
        self.assertEqual(config.default_auto_field, 'django.db.models.BigAutoField')

    def test_app_is_registered(self):
        config = apps.get_app_config('to_do_app')
        self.assertIsInstance(config, ToDoAppConfig)
        self.assertEqual(config.label, 'to_do_app')
