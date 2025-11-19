from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
]

CATEGORY_CHOICES = [
    ('Work', 'Work'),
    ('School', 'School'),
    ('Personal', 'Personal'),
]

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    # Toggle between pending/completed
    def toggle_status(self):
        if self.status == 'completed':
            self.status = 'pending'
            self.completed_at = None
        else:
            self.status = 'completed'
            self.completed_at = timezone.now()
        self.save()

    @classmethod
    def completed_today(cls, user):
        today = timezone.now().date()
        return cls.objects.filter(
            user=user,
            status='completed',
            completed_at__date=today
        ).count()


