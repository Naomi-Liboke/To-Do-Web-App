from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # --- CATEGORY FIELD (Existing) ---
    CATEGORY_CHOICES = [
        ('Work', 'Work'),
        ('School', 'School'),
        ('Personal', 'Personal'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Personal')
    # --- 🟢 STATUS TRACKING FIELD (NEW) ---
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETE', 'Complete'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TODO',
    )

    # --- 🔴 TASK PRIORITY FIELD (NEW) ---
    PRIORITY_CHOICES = [
        ('H', 'High 🔴'),
        ('M', 'Medium 🟡'),
        ('L', 'Low 🟢'),
    ]
    priority = models.CharField(
        max_length=1,
        choices=PRIORITY_CHOICES,
        default='M',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



    