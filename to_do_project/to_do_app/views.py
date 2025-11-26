from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from django.urls import reverse_lazy
from datetime import datetime, timedelta
from calendar import monthrange
import calendar as cal
from .models import Task, Profile
from .forms import ProfileForm

# Password Reset Views at the TOP to avoid circular imports
class CustomPasswordResetView(PasswordResetView):
    template_name = 'to_do_app/password_reset.html'
    email_template_name = 'to_do_app/password_reset_email.html'
    subject_template_name = 'to_do_app/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'to_do_app/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'to_do_app/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'to_do_app/password_reset_complete.html'

def login_view(request):
    # If user is already logged in, redirect to task list
    if request.user.is_authenticated:
        return redirect('task_list')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'to_do_app/login.html')

def register_view(request):
    # If user is already logged in, redirect to task list
    if request.user.is_authenticated:
        return redirect('task_list')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validation
        if not username or not email or not password1:
            messages.error(request, 'All fields are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        elif len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            try:
                # Create user with email and log them in
                user = User.objects.create_user(
                    username=username, 
                    email=email, 
                    password=password1
                )
                login(request, user)
                messages.success(request, f'Account created for {user.username}!')
                return redirect('task_list')
            except Exception as e:
                messages.error(request, 'Error creating account. Please try again.')
    
    return render(request, 'to_do_app/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

@login_required(login_url='/login/')
def task_list(request):
    # Get search query and category filter from URL parameters
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    
    # Get tasks for the current user
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # Apply search filter if query exists
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Apply category filter if selected
    if category_filter:
        tasks = tasks.filter(category__iexact=category_filter)
    
    # Calculate stats (these will reflect the filtered tasks)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    completed_today = Task.completed_today(request.user)
    
    # Get unique categories for the filter dropdown
    categories = Task.objects.filter(user=request.user).values_list('category', flat=True).distinct()
    
    context = {
        'tasks': tasks,
        'completed_today': completed_today,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, 'to_do_app/task_list.html', context)

@login_required(login_url='/login/')
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        due_date = request.POST.get('due_date')
        
        # New: Retrieve the uploaded file from request.FILES
        attachment = request.FILES.get('attachment') # Correctly retrieve the file
        
        if title:  # Basic validation
            Task.objects.create(
                user=request.user,
                title=title,
                description=description,
                category=category,
                due_date=due_date if due_date else None,
                attachment=attachment # Pass the file object to the model
            )
            messages.success(request, 'Task added successfully!')
            return redirect('task_list')
        else:
            messages.error(request, 'Task title is required.')
    
    return render(request, 'to_do_app/add_task.html')

@login_required(login_url='/login/')
def edit_task(request, task_id):
    # Get the task, ensuring it belongs to the current user
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.category = request.POST.get('category')
        task.due_date = request.POST.get('due_date') if request.POST.get('due_date') else None 
        
        # Handle file upload/replacement
        if 'attachment' in request.FILES:
            # New file uploaded: update the attachment
            task.attachment = request.FILES['attachment']
        # Note: To remove an existing file, you would typically need an extra checkbox 
        # or button in the template that signals the intention to clear the field.
        # Without that, if the user submits the form without selecting a file, 
        # the existing task.attachment value is preserved (due to not explicitly being set to None).
        
        task.save()
        
        messages.success(request, 'Task updated successfully!')
        return redirect('task_list')
    
    return render(request, 'to_do_app/edit_task.html', {'task': task})

@login_required(login_url='/login/')
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    messages.success(request, 'Task deleted successfully!')
    return redirect('task_list')

@login_required(login_url='/login/')
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    # Use your model's toggle_status method
    task.toggle_status()
    
    status = "completed" if task.completed else "marked as pending"
    messages.success(request, f'Task {status}!')
    return redirect('task_list')

@login_required(login_url='/login/')
def calendar_view(request):
    # Get the month from query parameters or use current month
    month_str = request.GET.get('month')
    if month_str:
        try:
            current_date = datetime.strptime(month_str, '%Y-%m').date()
        except ValueError:
            current_date = timezone.now().date()
    else:
        current_date = timezone.now().date()
    
    # Set up calendar data
    year = current_date.year
    month = current_date.month
    
    # Get first and last day of the month
    first_day = current_date.replace(day=1)
    last_day = first_day.replace(day=monthrange(year, month)[1])
    
    # Get all tasks with due dates for this month for the current user
    tasks = Task.objects.filter(
        user=request.user,
        due_date__gte=first_day,
        due_date__lte=last_day + timedelta(days=1)
    ).order_by('due_date')
    
    # Create calendar structure
    cal_obj = cal.Calendar(firstweekday=6)  # Sunday first
    month_days = cal_obj.monthdayscalendar(year, month)
    
    calendar_weeks = []
    today = timezone.now().date()
    
    for week in month_days:
        calendar_week = []
        for day in week:
            if day == 0:  # Day from previous/next month
                calendar_week.append({
                    'day': '',
                    'month': 'other',
                    'tasks': [],
                    'is_today': False
                })
            else:
                day_date = current_date.replace(day=day)
                # FIXED: Remove .date() since task.due_date is already a date object
                day_tasks = [task for task in tasks if task.due_date == day_date]
                
                calendar_week.append({
                    'day': day,
                    'month': 'current',
                    'month_num': month,
                    'tasks': day_tasks,
                    'is_today': day_date == today
                })
        calendar_weeks.append(calendar_week)
    
    # Get tasks for selected date or today
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today
    
    # FIXED: Remove __date lookup since due_date is a DateField
    daily_tasks = Task.objects.filter(
        user=request.user,
        due_date=selected_date
    ).order_by('due_date')
    
    # Calculate summary statistics
    total_scheduled = Task.objects.filter(
        user=request.user,
        due_date__isnull=False
    ).count()
    
    overdue_count = Task.objects.filter(
        user=request.user,
        due_date__lt=today, 
        completed=False
    ).count()
    
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    # FIXED: Remove __date lookup for range query
    due_this_week = Task.objects.filter(
        user=request.user,
        due_date__range=[start_of_week, end_of_week]
    ).count()
    
    completed_count = Task.objects.filter(
        user=request.user,
        completed=True
    ).count()
    
    # Get all tasks with due dates for the list view
    tasks_with_due_dates = Task.objects.filter(
        user=request.user,
        due_date__isnull=False
    ).order_by('due_date')
    
    context = {
        'current_month': first_day.strftime('%B'),
        'current_year': year,
        'current_month_num': month,
        'calendar': calendar_weeks,
        'prev_month': (first_day - timedelta(days=1)).strftime('%Y-%m'),
        'next_month': (last_day + timedelta(days=1)).strftime('%Y-%m'),
        'today': today.strftime('%Y-%m'),
        'selected_date': selected_date,
        'daily_tasks': daily_tasks,
        'total_scheduled': total_scheduled,
        'overdue_count': overdue_count,
        'due_this_week': due_this_week,
        'completed_count': completed_count,
        'tasks_with_due_dates': tasks_with_due_dates,
    }
    
    return render(request, 'to_do_app/calendar.html', context)

@login_required(login_url='/login/')
def profile_view(request):
    # Get or create profile for the user
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Calculate statistics for the template
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, completed=True).count()
    pending_tasks = Task.objects.filter(user=request.user, completed=False).count()
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
    
    context = {
        'profile_form': profile_form,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'to_do_app/profile.html', context)

@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important: keeps user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'to_do_app/change_password.html', {'form': form})