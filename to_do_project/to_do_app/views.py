from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Task
from django.db.models import Q 

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
    # Get tasks with due dates for the current user
    tasks_with_due_dates = Task.objects.filter(
        user=request.user,
        due_date__isnull=False
    ).order_by('due_date')
    
    # Get tasks by due date for calendar display
    tasks_by_date = {}
    for task in tasks_with_due_dates:
        date_str = task.due_date.strftime('%Y-%m-%d')
        if date_str not in tasks_by_date:
            tasks_by_date[date_str] = []
        tasks_by_date[date_str].append(task)
    
    context = {
        'tasks_with_due_dates': tasks_with_due_dates,
        'tasks_by_date': tasks_by_date,
    }
    return render(request, 'to_do_app/calendar.html', context)