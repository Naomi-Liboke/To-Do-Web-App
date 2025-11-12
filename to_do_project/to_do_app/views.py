from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Task

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
    # Get tasks for the current user
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate stats
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(completed=True).count()
    pending_tasks = total_tasks - completed_tasks
    completed_today = Task.completed_today(request.user)
    
    context = {
        'tasks': tasks,
        'completed_today': completed_today,
        'total_tasks': total_tasks,
        'pending_tasks': pending_tasks,
    }
    return render(request, 'to_do_app/task_list.html', context)

@login_required(login_url='/login/')
def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        
        if title:  # Basic validation
            Task.objects.create(
                user=request.user,
                title=title,
                description=description,
                category=category
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