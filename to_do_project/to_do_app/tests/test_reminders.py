from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from to_do_app.models import Task
from to_do_app.services import reminders
from unittest.mock import patch

User = get_user_model()


class GetUserPendingTasksTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")

    def test_returns_tasks_due_today(self):
        today = timezone.now().date()
        task = Task.objects.create(user=self.user, title="Due today", due_date=today, completed=False)
        tasks = reminders.get_user_pending_tasks(self.user)
        self.assertIn(task, tasks)

    def test_excludes_completed_tasks(self):
        today = timezone.now().date()
        task = Task.objects.create(user=self.user, title="Completed", due_date=today, completed=True)
        tasks = reminders.get_user_pending_tasks(self.user)
        self.assertNotIn(task, tasks)

    def test_includes_future_tasks_with_window_days(self):
        future = timezone.now().date() + timezone.timedelta(days=3)
        task = Task.objects.create(user=self.user, title="Future", due_date=future, completed=False)
        tasks = reminders.get_user_pending_tasks(self.user, window_days=5)
        self.assertIn(task, tasks)

    def test_excludes_future_tasks_without_window_days(self):
        future = timezone.now().date() + timezone.timedelta(days=3)
        task = Task.objects.create(user=self.user, title="Future", due_date=future, completed=False)
        tasks = reminders.get_user_pending_tasks(self.user)
        self.assertNotIn(task, tasks)


class BuildPendingEmailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")

    @patch("to_do_app.services.reminders.render_to_string", return_value="<p>Email body</p>")
    def test_build_pending_email_returns_subject_and_html(self, mock_render):
        tasks = [Task(title="Task1", user=self.user)]
        subject, html_body = reminders.build_pending_email(self.user, tasks)

        self.assertEqual(subject, "⏰ Your FocusFlow Task Reminder")
        self.assertEqual(html_body, "<p>Email body</p>")

        # Ensure render_to_string was called with correct template and context
        mock_render.assert_called_once()
        args, kwargs = mock_render.call_args
        self.assertEqual(args[0], "to_do_app/reminder.html")
        # The function may be called with the context as a positional arg or as a kwarg
        if len(args) > 1:
            context = args[1]
        else:
            context = kwargs.get('context', {})

        self.assertEqual(context.get("user"), self.user)
        self.assertEqual(context.get("tasks"), tasks)
