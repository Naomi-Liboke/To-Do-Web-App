from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from to_do_app.models import Task, Profile

class TaskViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.login(username='tester', password='pass')

    def test_add_task_valid(self):
        response = self.client.post(reverse('add_task'), {
            'title': 'New Task',
            'category': 'Work',
            'description': 'Test description',
        })
        self.assertRedirects(response, reverse('task_list'))
        self.assertTrue(Task.objects.filter(title='New Task').exists())

    def test_toggle_task_twice(self):
        task = Task.objects.create(user=self.user, title='Toggle Twice', category='Work')
        self.client.get(reverse('toggle_task', args=[task.id]))
        task.refresh_from_db()
        self.assertTrue(task.completed)
        self.client.get(reverse('toggle_task', args=[task.id]))
        task.refresh_from_db()
        self.assertFalse(task.completed)
        
    def test_add_task_invalid(self):
        response = self.client.post(reverse('add_task'), {
            'title': '',  # Missing title
            'category': 'Work',
        })
        self.assertContains(response, 'Task title is required.')

    def test_edit_task_updates_fields(self):
        task = Task.objects.create(user=self.user, title='Old Title', category='Work')
        response = self.client.post(reverse('edit_task', args=[task.id]), {
            'title': 'Updated Title',
            'category': 'Personal',
        })
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Title')
        self.assertEqual(task.category, 'Personal')

    def test_edit_task_replaces_attachment(self):
        task = Task.objects.create(user=self.user, title='File Task', category='Work')
        file = SimpleUploadedFile("new.txt", b"new content")
        response = self.client.post(reverse('edit_task', args=[task.id]), {
            'title': 'File Task',
            'category': 'Work',
            'attachment': file,
        })
        task.refresh_from_db()
        self.assertTrue(task.attachment.name.endswith(".txt"))

    def test_delete_task(self):
        task = Task.objects.create(user=self.user, title='Delete Me', category='Work')
        response = self.client.get(reverse('delete_task', args=[task.id]))
        self.assertRedirects(response, reverse('task_list'))
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_toggle_task(self):
        task = Task.objects.create(user=self.user, title='Toggle Me', category='Work')
        response = self.client.get(reverse('toggle_task', args=[task.id]))
        task.refresh_from_db()
        self.assertTrue(task.completed)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.login(username='tester', password='pass')

    def test_profile_view_get(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')

    def test_profile_view_post_updates(self):
        response = self.client.post(reverse('profile'), {
            'first_name': 'John',
            'last_name': 'Dave',
            'bio': 'Hello world',
        })
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.first_name, 'John')
        self.assertEqual(self.user.profile.last_name, 'Dave')
        self.assertEqual(self.user.profile.bio, 'Hello world')

    def test_remove_avatar(self):
        profile = self.user.profile
        file = SimpleUploadedFile("avatar.png", b"imgdata")
        profile.avatar = file
        profile.save()
        response = self.client.get(reverse('remove_avatar'))
        profile.refresh_from_db()
        self.assertFalse(profile.avatar)

    def test_delete_account_wrong_password(self):
        response = self.client.post(reverse('delete_account'), {'password': 'wrong'})
        self.assertTrue(User.objects.filter(username='tester').exists())

    def test_delete_account_correct_password(self):
        response = self.client.post(reverse('delete_account'), {'password': 'pass'})
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(User.objects.filter(username='tester').exists())


class CalendarViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.client.login(username='tester', password='pass')

    def test_calendar_view_default(self):
        response = self.client.get(reverse('calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'calendar')

    def test_calendar_view_with_date_param(self):
        response = self.client.get(reverse('calendar') + '?date=2025-12-04')
        self.assertEqual(response.status_code, 200)

    def test_calendar_view_invalid_date_param(self):
        response = self.client.get(reverse('calendar') + '?date=invalid-date')
        self.assertEqual(response.status_code, 200)  # should still render

class ReminderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='pass', email='tester@example.com')
        self.client.login(username='tester', password='pass')

    def test_send_reminder_with_tasks(self):
        from django.utils import timezone
        Task.objects.create(user=self.user, title='Pending', category='Work', due_date=timezone.now().date())
        response = self.client.get(reverse('send_reminder_now'))
        self.assertContains(response, 'Reminder email sent to you!')

    def test_send_reminder_now_no_tasks(self):
        response = self.client.get(reverse('send_reminder_now'))
        self.assertContains(response, 'No pending tasks to remind')

    def test_test_email(self):
        response = self.client.get(reverse('test_email'))
        self.assertContains(response, 'Test email sent!')

    def test_send_reminder_user_without_email(self):
        self.user.email = ''
        self.user.save()
        Task.objects.create(user=self.user, title='Pending', category='Work')
        response = self.client.get(reverse('send_reminder_now'))
        # Depending on your view logic, assert safe fallback
        self.assertEqual(response.status_code, 200)

class ChangePasswordViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='oldpass')
        self.client.login(username='tester', password='oldpass')

    def test_change_password_valid(self):
        response = self.client.post(reverse('change_password'), {
            'old_password': 'oldpass',
            'new_password1': 'NewStrongPass123!',
            'new_password2': 'NewStrongPass123!',
        })
        # Should redirect to profile after success
        self.assertRedirects(response, reverse('profile'))
        # User should now be able to login with new password
        self.client.logout()
        login_success = self.client.login(username='tester', password='NewStrongPass123!')
        self.assertTrue(login_success)

    def test_change_password_invalid(self):
        response = self.client.post(reverse('change_password'), {
            'old_password': 'wrongpass',
            'new_password1': 'NewStrongPass123!',
            'new_password2': 'NewStrongPass123!',
        })
        # Should re-render form with error
        self.assertContains(response, 'Please correct the error below.')
        # Password should remain unchanged
        self.client.logout()
        login_old = self.client.login(username='tester', password='oldpass')
        self.assertTrue(login_old)

    def test_change_password_mismatched_new_passwords(self):
        response = self.client.post(reverse('change_password'), {
            'old_password': 'oldpass',
            'new_password1': 'NewPass123!',
            'new_password2': 'MismatchPass123!',
        })
        self.assertContains(response, 'The two password fields didn’t match.')