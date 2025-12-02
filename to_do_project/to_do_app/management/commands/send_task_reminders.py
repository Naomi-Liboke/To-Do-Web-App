from to_do_app.utils.email import send_html_email_with_logo
from to_do_app.services.reminders import build_pending_email

class Command(BaseCommand):
    help = "Send email reminders for pending tasks"

    def handle(self, *args, **options):
        for user in User.objects.exclude(email='').iterator():
            tasks = get_user_pending_tasks(user, window_days=options['window_days'])
            if tasks.exists():
                subject, html_body = build_pending_email(user, tasks)
                send_html_email_with_logo(
                    subject=subject,
                    template_name="emails/reminder.html",
                    context={"user": user, "tasks": tasks},
                    recipient=user.email
                )
                self.stdout.write(self.style.SUCCESS(f"Sent reminder to {user.username}"))