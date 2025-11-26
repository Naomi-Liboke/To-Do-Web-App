from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Task(models.Model):
    # Each task belongs to a user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Task details
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Task category
    CATEGORY_CHOICES = [
        ('Work', 'Work'),
        ('School', 'School'),
        ('Personal', 'Personal'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    # Task status
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Due date for scheduling
    due_date = models.DateField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New Field for File Attachment
    # 'upload_to' specifies a subdirectory within your MEDIA_ROOT
    attachment = models.FileField(
        upload_to='task_attachments/', 
        null=True, 
        blank=True
    )
    
    # String representation
    def __str__(self):
        return f"{self.title} ({'Done' if self.completed else 'Pending'})"

    # Toggle task status
    def toggle_status(self):
        self.completed = not self.completed
        self.completed_at = timezone.now() if self.completed else None
        self.save()

    # Check if task is overdue
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False

    # Days until due (positive = days left, negative = days overdue)
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now().date()
            return delta.days
        return None

    # Get due status text
    def get_due_status(self):
        if not self.due_date:
            return "No due date"
        if self.completed:
            return "Completed"
        days = self.days_until_due()
        if days < 0:
            return f"Overdue by {-days} days"
        elif days == 0:
            return "Due today"
        elif days == 1:
            return "Due tomorrow"
        else:
            return f"Due in {days} days"

    # Count tasks completed today (class method for dashboard)
    @classmethod
    def completed_today(cls, user):
        today = timezone.now().date()
        return cls.objects.filter(user=user, completed=True, completed_at__date=today).count()

    # Count overdue tasks
    @classmethod
    def overdue_count(cls, user):
        today = timezone.now().date()
        return cls.objects.filter(
            user=user, 
            completed=False, 
            due_date__lt=today
        ).count()

    # Count tasks due today
    @classmethod
    def due_today_count(cls, user):
        today = timezone.now().date()
        return cls.objects.filter(
            user=user, 
            completed=False, 
            due_date=today
        ).count()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    email_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()