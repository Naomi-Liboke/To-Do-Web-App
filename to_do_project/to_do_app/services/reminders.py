from django.utils import timezone
from django.contrib.auth import get_user_model
from to_do_app.models import Task  # use absolute import
from django.template.loader import render_to_string

User = get_user_model()

def get_user_pending_tasks(user, window_days=0):
    today = timezone.now().date()
    if window_days > 0:
        end_date = today + timezone.timedelta(days=window_days)
        return Task.objects.filter(user=user, completed=False, due_date__lte=end_date)
    return Task.objects.filter(user=user, completed=False, due_date__lte=today)

from django.template.loader import render_to_string

def build_pending_email(user, tasks):
    subject = "⏰ Your FocusFlow Task Reminder"
    html_body = render_to_string("to_do_app/reminder.html", {
        "user": user,
        "tasks": tasks
    })
    return subject, html_body
