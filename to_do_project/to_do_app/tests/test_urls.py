from django.test import SimpleTestCase
from django.urls import reverse, resolve
from to_do_app import views
from to_do_app.views import test_email
from django.contrib.auth import views as auth_views


class UrlsTests(SimpleTestCase):
    def test_task_list_url(self):
        url = reverse('task_list')
        self.assertEqual(resolve(url).func, views.task_list)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, views.login_view)

    def test_register_url(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register_view)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, views.logout_view)

    def test_add_task_url(self):
        url = reverse('add_task')
        self.assertEqual(resolve(url).func, views.add_task)

    def test_edit_task_url(self):
        url = reverse('edit_task', args=[1])
        self.assertEqual(resolve(url).func, views.edit_task)

    def test_delete_task_url(self):
        url = reverse('delete_task', args=[1])
        self.assertEqual(resolve(url).func, views.delete_task)

    def test_toggle_task_url(self):
        url = reverse('toggle_task', args=[1])
        self.assertEqual(resolve(url).func, views.toggle_task)

    def test_calendar_url(self):
        url = reverse('calendar')
        self.assertEqual(resolve(url).func, views.calendar_view)

    def test_profile_url(self):
        url = reverse('profile')
        self.assertEqual(resolve(url).func, views.profile_view)

    def test_change_password_url(self):
        url = reverse('change_password')
        self.assertEqual(resolve(url).func, views.change_password)

    def test_test_email_url(self):
        url = reverse('test_email')
        self.assertEqual(resolve(url).func, test_email)

    def test_remove_avatar_url(self):
        url = reverse('remove_avatar')
        self.assertEqual(resolve(url).func, views.remove_avatar)

    def test_delete_account_url(self):
        url = reverse('delete_account')
        self.assertEqual(resolve(url).func, views.delete_account)

    def test_send_reminder_now_url(self):
        url = reverse('send_reminder_now')
        self.assertEqual(resolve(url).func, views.send_reminder_now)

    # Password reset URLs
    def test_password_reset_url(self):
        url = reverse('password_reset')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetView)

    def test_password_reset_done_url(self):
        url = reverse('password_reset_done')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetDoneView)

    def test_password_reset_confirm_url(self):
        url = reverse('password_reset_confirm', args=['uidb64', 'token'])
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetConfirmView)

    def test_password_reset_complete_url(self):
        url = reverse('password_reset_complete')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetCompleteView)
