from django.test import TestCase, RequestFactory
from to_do_app.context_processors import show_welcome


class ShowWelcomeContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_show_welcome_true_in_session(self):
        request = self.factory.get('/')
        request.session = {'show_welcome': True}
        context = show_welcome(request)
        self.assertTrue(context['show_welcome'])
        # key should be popped from session
        self.assertNotIn('show_welcome', request.session)

    def test_show_welcome_false_in_session(self):
        request = self.factory.get('/')
        request.session = {'show_welcome': False}
        context = show_welcome(request)
        self.assertFalse(context['show_welcome'])
        # key should be popped from session
        self.assertNotIn('show_welcome', request.session)

    def test_show_welcome_key_missing(self):
        request = self.factory.get('/')
        request.session = {}
        context = show_welcome(request)
        self.assertFalse(context['show_welcome'])

    def test_show_welcome_session_exception(self):
        class BadSession(dict):
            def pop(self, *args, **kwargs):
                raise Exception("Session error")

        request = self.factory.get('/')
        request.session = BadSession()
        context = show_welcome(request)
        self.assertFalse(context['show_welcome'])
