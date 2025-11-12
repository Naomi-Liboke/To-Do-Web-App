from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # String representation
    def __str__(self):
        return f"{self.title} ({'Done' if self.completed else 'Pending'})"

    # Toggle task status
    def toggle_status(self):
        self.completed = not self.completed
        self.completed_at = timezone.now() if self.completed else None
        self.save()

    # Count tasks completed today (class method for dashboard)
    @classmethod
    def completed_today(cls, user):
        today = timezone.now().date()
        return cls.objects.filter(user=user, completed=True, completed_at__date=today).count()

