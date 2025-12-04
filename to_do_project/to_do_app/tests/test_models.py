from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

from to_do_app.models import Task, Profile


class TaskModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')

    def test_str_representation(self):
        task = Task.objects.create(user=self.user, title='My Task', category='Work')
        self.assertEqual(str(task), "My Task (Pending)")
        task.toggle_status()
        self.assertIn("Done", str(task))

    def test_get_due_status_no_due_date(self):
        task = Task.objects.create(user=self.user, title='No Due', category='Personal')
        self.assertEqual(task.get_due_status(), "No due date")

    def test_days_until_due_none(self):
        task = Task.objects.create(user=self.user, title="No Due", category="Work")
        self.assertIsNone(task.days_until_due())

    def test_get_due_status_future(self):
        future_date = timezone.now().date() + timedelta(days=5)
        task = Task.objects.create(user=self.user, title="Future", category="Work", due_date=future_date)
        self.assertEqual(task.get_due_status(), "Due in 5 days")

    def test_get_due_status_completed(self):
        today = timezone.now().date()
        task = Task.objects.create(user=self.user, title='Completed', category='Work', due_date=today)
        task.toggle_status()
        self.assertEqual(task.get_due_status(), "Completed")

    def test_attachment_field(self):
        file = SimpleUploadedFile("test.txt", b"file_content")
        task = Task.objects.create(user=self.user, title="With File", category="Work", attachment=file)
        self.assertTrue(task.attachment.name.startswith("task_attachments/"))
        self.assertTrue(task.attachment.name.endswith(".txt"))

    def test_count_helpers_no_tasks(self):
        self.assertEqual(Task.completed_today(self.user), 0)
        self.assertEqual(Task.overdue_count(self.user), 0)
        self.assertEqual(Task.due_today_count(self.user), 0)

    def test_get_due_status_overdue(self):
        yesterday = timezone.now().date() - timedelta(days=3)
        task = Task.objects.create(user=self.user, title='Late Task', category='Work', due_date=yesterday)
        self.assertIn("Overdue by 3 days", task.get_due_status())

    def test_toggle_status_multiple_times(self):
        task = Task.objects.create(user=self.user, title='Toggle', category='Work')
        # First toggle → completed
        task.toggle_status()
        self.assertTrue(task.completed)
        self.assertIsNotNone(task.completed_at)
        # Second toggle → back to pending
        task.toggle_status()
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)

    def test_count_helpers_with_tasks(self):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        # Completed today
        Task.objects.create(user=self.user, title='C1', category='Work',
                            completed=True, completed_at=timezone.now())
        # Completed yesterday
        Task.objects.create(user=self.user, title='C2', category='Work',
                            completed=True, completed_at=timezone.now() - timedelta(days=1))
        # Overdue
        Task.objects.create(user=self.user, title='O1', category='Work',
                            due_date=yesterday, completed=False)
        # Due today
        Task.objects.create(user=self.user, title='D1', category='Work',
                            due_date=today, completed=False)

        self.assertEqual(Task.completed_today(self.user), 1)
        self.assertEqual(Task.overdue_count(self.user), 1)
        self.assertEqual(Task.due_today_count(self.user), 1)

class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')

    def test_str_representation(self):
        profile = self.user.profile
        self.assertEqual(str(profile), "tester\'s Profile")

    def test_full_name_with_names(self):
        profile = self.user.profile
        profile.first_name = "Test"
        profile.last_name = "User"
        profile.save()
        self.assertEqual(profile.full_name, "Test User")

    def test_optional_fields(self):
        profile = self.user.profile
        profile.bio = "Hello world"
        profile.location = "Johannesburg"
        profile.phone = "123456789"
        profile.website = "https://example.com"
        profile.save()
        self.assertEqual(profile.bio, "Hello world")
        self.assertEqual(profile.location, "Johannesburg")
        self.assertEqual(profile.phone, "123456789")
        self.assertEqual(profile.website, "https://example.com")

    def test_profile_created_signal(self):
        user = User.objects.create_user(username='signaluser', password='pw')
        self.assertTrue(hasattr(user, 'profile'))

    def test_profile_saved_signal(self):
        user = User.objects.create_user(username='saveuser', password='pw')
        profile = user.profile
        profile.bio = "Signal test"
        user.save()  # triggers save_user_profile
        profile.refresh_from_db()
        self.assertEqual(profile.bio, "Signal test")
