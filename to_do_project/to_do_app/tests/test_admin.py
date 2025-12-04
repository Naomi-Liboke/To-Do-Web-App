from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from to_do_app.models import Profile, Task
from to_do_app.admin import ProfileAdmin, TaskAdmin
from django.contrib.admin.sites import AdminSite

class ProfileAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ProfileAdmin(Profile, self.site)
        self.user = User.objects.create_user(
            username='tester', password='pass', email='tester@example.com'
        )
        self.profile = self.user.profile

    def test_full_name_display_with_names(self):
        self.profile.first_name = "John"
        self.profile.last_name = "Dave"
        self.profile.save()
        result = self.admin.full_name_display(self.profile)
        self.assertEqual(result, "John Dave")

    def test_full_name_display_fallback(self):
        result = self.admin.full_name_display(self.profile)
        self.assertEqual(result, "tester")

    def test_email_display(self):
        result = self.admin.email_display(self.profile)
        self.assertEqual(result, "tester@example.com")

    def test_has_avatar_false(self):
        self.assertFalse(self.admin.has_avatar(self.profile))

    def test_has_avatar_true_and_preview(self):
        file = SimpleUploadedFile("avatar.png", b"imgdata")
        self.profile.avatar = file
        self.profile.save()
        self.assertTrue(self.admin.has_avatar(self.profile))
        preview = self.admin.avatar_preview(self.profile)
        self.assertIn("img", preview)

    def test_avatar_preview_no_file(self):
        self.profile.avatar = None
        self.profile.save()
        preview = self.admin.avatar_preview(self.profile)
        self.assertEqual(preview, "No avatar uploaded")

    def test_created_date_and_last_updated(self):
        created = self.admin.created_date(self.profile)
        self.assertEqual(created, self.user.date_joined)
        # last_login is None initially
        last = self.admin.last_updated(self.profile)
        self.assertEqual(last, "Never")
        # simulate login
        self.user.last_login = timezone.now()
        self.user.save()
        last = self.admin.last_updated(self.profile)
        self.assertEqual(last.date(), timezone.now().date())

    

class TaskAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = TaskAdmin(Task, self.site)
        self.user = User.objects.create_user(username='tester', password='pass')

    def test_status_display_completed(self):
        task = Task.objects.create(user=self.user, title="Done", category="Work", completed=True)
        result = self.admin.status_display(task)
        self.assertIn("Completed", result)

    def test_status_display_overdue(self):
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        task = Task.objects.create(user=self.user, title="Late", category="Work", due_date=yesterday)
        result = self.admin.status_display(task)
        self.assertIn("Overdue", result)

    def test_status_display_pending(self):
        task = Task.objects.create(user=self.user, title="Pending", category="Work")
        result = self.admin.status_display(task)
        self.assertIn("Pending", result)

    def test_due_date_display_no_due_date(self):
        task = Task.objects.create(user=self.user, title="NoDue", category="Work")
        result = self.admin.due_date_display(task)
        self.assertEqual(result, "No due date")

    def test_due_date_display_today(self):
        today = timezone.now().date()
        task = Task.objects.create(user=self.user, title="Today", category="Work", due_date=today)
        result = self.admin.due_date_display(task)
        self.assertIn("Today", result)

    def test_due_date_display_overdue(self):
        yesterday = timezone.now().date() - timezone.timedelta(days=2)
        task = Task.objects.create(user=self.user, title="Late", category="Work", due_date=yesterday)
        result = self.admin.due_date_display(task)
        self.assertIn("overdue", result)

    def test_due_date_display_future(self):
        future = timezone.now().date() + timezone.timedelta(days=5)
        task = Task.objects.create(user=self.user, title="Future", category="Work", due_date=future)
        result = self.admin.due_date_display(task)
        self.assertEqual(result, future.strftime('%Y-%m-%d'))

    def test_has_attachment_and_preview(self):
        file = SimpleUploadedFile("doc.txt", b"content")
        task = Task.objects.create(user=self.user, title="Attach", category="Work", attachment=file)
        self.assertTrue(self.admin.has_attachment(task))
        preview = self.admin.attachment_preview(task)
        self.assertIn("Download", preview)

    def test_attachment_preview_no_file(self):
        task = Task.objects.create(user=self.user, title="NoAttach", category="Work")
        preview = self.admin.attachment_preview(task)
        self.assertEqual(preview, "No attachment")

    def test_overdue_status_and_days_until_due_display(self):
        yesterday = timezone.now().date() - timezone.timedelta(days=3)
        task = Task.objects.create(user=self.user, title="Late", category="Work", due_date=yesterday)
        overdue = self.admin.overdue_status(task)
        self.assertIn("Overdue", overdue)
        days_display = self.admin.days_until_due_display(task)
        self.assertIn("Overdue", days_display)

        today = timezone.now().date()
        task2 = Task.objects.create(user=self.user, title="Today", category="Work", due_date=today)
        self.assertEqual(self.admin.days_until_due_display(task2), "Due today")

        tomorrow = timezone.now().date() + timezone.timedelta(days=1)
        task3 = Task.objects.create(user=self.user, title="Tomorrow", category="Work", due_date=tomorrow)
        self.assertEqual(self.admin.days_until_due_display(task3), "Due tomorrow")

        future = timezone.now().date() + timezone.timedelta(days=5)
        task4 = Task.objects.create(user=self.user, title="Future", category="Work", due_date=future)
        self.assertIn("Due in 5 days", self.admin.days_until_due_display(task4))

        task5 = Task.objects.create(user=self.user, title="NoDue", category="Work")
        self.assertEqual(self.admin.days_until_due_display(task5), "No due date")
