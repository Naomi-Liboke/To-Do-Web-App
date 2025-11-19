from .models import Task
from django.utils import timezone

def task_stats(request):
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user)
        return {
            'completed_today': tasks.filter(
                status='completed',
                completed_at__date=timezone.now().date()
            ).count(),
            'total_tasks': tasks.count(),
            'pending_tasks': tasks.exclude(status='completed').count(),
        }
    return {
        'completed_today': 0,
        'total_tasks': 0,
        'pending_tasks': 0,
    }
