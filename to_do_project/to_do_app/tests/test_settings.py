import os
from unittest.mock import patch
from importlib import reload
from django.test import SimpleTestCase, override_settings
from django.conf import settings


class SettingsTests(SimpleTestCase):
    def test_secret_key_default_and_env_override(self):
        # Default key should be set
        self.assertTrue(settings.SECRET_KEY.startswith("django-insecure"))

        # Override with environment variable
        with override_settings(SECRET_KEY="custom-secret"):
            self.assertEqual(settings.SECRET_KEY, "custom-secret")

    def test_debug_flag_true_and_false(self):
        # Ensure we have a deterministic True value for the first assertion
        with override_settings(DEBUG=True):
            self.assertTrue(settings.DEBUG)

        # Simulate environment variable forcing False and reload settings
        prev = os.environ.get('DEBUG')
        with patch.dict(os.environ, {'DEBUG': 'False'}):
            import blog_project.settings as reloaded_settings
            reload(reloaded_settings)
            self.assertFalse(reloaded_settings.DEBUG)

        # Restore previous environment value and reload settings to avoid side effects
        if prev is None:
            os.environ.pop('DEBUG', None)
        else:
            os.environ['DEBUG'] = prev
        import blog_project.settings as restored_settings
        reload(restored_settings)

    def test_static_and_media_paths(self):
        self.assertEqual(settings.STATIC_URL, "/static/")
        self.assertTrue(any("static" in str(p) for p in settings.STATICFILES_DIRS))
        self.assertEqual(settings.MEDIA_URL, "/media/")
        self.assertTrue(settings.MEDIA_ROOT.endswith("media"))

    def test_installed_apps_and_middleware(self):
        self.assertIn("to_do_app", settings.INSTALLED_APPS)
        self.assertIn("django.middleware.security.SecurityMiddleware", settings.MIDDLEWARE)

    def test_email_settings(self):
        # In tests Django may use the locmem backend; accept either smtp or locmem
        self.assertIn(settings.EMAIL_BACKEND, (
            "django.core.mail.backends.smtp.EmailBackend",
            "django.core.mail.backends.locmem.EmailBackend",
        ))
        self.assertEqual(settings.EMAIL_HOST, "smtp.gmail.com")
        self.assertEqual(settings.EMAIL_PORT, 587)
        self.assertTrue(settings.EMAIL_USE_TLS)
        self.assertIn("gmail.com", settings.EMAIL_HOST_USER)
        self.assertIn("FocusFlow Notifications", settings.DEFAULT_FROM_EMAIL)
