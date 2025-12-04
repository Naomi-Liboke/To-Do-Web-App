from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Profile, Task

# Custom admin for Profile
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name_display', 'email_display', 'title', 'has_avatar', 'email_notifications')
    list_filter = ('email_notifications',)
    search_fields = ('user__username', 'first_name', 'last_name', 'user__email', 'location', 'title')
    readonly_fields = ('user', 'created_date', 'last_updated')
    list_per_page = 25
    
    # Group fields in admin form
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'avatar', 'avatar_preview')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'title', 'bio')
        }),
        ('Contact Information', {
            'fields': ('location', 'birth_date', 'phone', 'website')
        }),
        ('Preferences', {
            'fields': ('email_notifications',)
        }),
    )
    
    def full_name_display(self, obj):
        """Display full name in admin list"""
        return obj.full_name if obj.full_name != obj.user.username else obj.user.username
    full_name_display.short_description = 'Name'
    
    def email_display(self, obj):
        """Display user email in admin list"""
        return obj.user.email
    email_display.short_description = 'Email'
    
    def has_avatar(self, obj):
        """Check if profile has avatar"""
        return bool(obj.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = 'Has Avatar'
    
    def avatar_preview(self, obj):
        """Show avatar preview in admin"""
        if obj.avatar:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px; border-radius: 50%;" />', obj.avatar.url)
        return "No avatar uploaded"
    avatar_preview.short_description = 'Avatar Preview'
    
    def created_date(self, obj):
        """Show when user was created"""
        return obj.user.date_joined
    created_date.short_description = 'User Created'
    
    def last_updated(self, obj):
        """Show last login"""
        return obj.user.last_login or 'Never'
    last_updated.short_description = 'Last Login'

# Custom admin for Task
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status_display', 'due_date_display', 'has_attachment', 'created_at')
    list_filter = ('completed', 'category', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'completed_at', 'overdue_status', 'days_until_due_display')
    list_per_page = 25
    date_hierarchy = 'due_date'
    
    # Group fields in admin form
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'category')
        }),
        ('Task Status', {
            'fields': ('completed', 'completed_at', 'overdue_status', 'days_until_due_display')
        }),
        ('Scheduling', {
            'fields': ('due_date',)
        }),
        ('Attachments', {
            'fields': ('attachment', 'attachment_preview')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Makes this section collapsible
        }),
    )
    
    def status_display(self, obj):
        """Display status with color coding"""
        if obj.completed:
            return format_html('<span style="color: green; font-weight: bold;">✓ Completed</span>')
        elif obj.is_overdue():
            return format_html('<span style="color: red; font-weight: bold;">⚠ Overdue</span>')
        else:
            return format_html('<span style="color: orange;">Pending</span>')
    status_display.short_description = 'Status'
    
    def due_date_display(self, obj):
        """Display due date with formatting"""
        if not obj.due_date:
            return "No due date"
        
        today = timezone.now().date()
        if obj.due_date == today:
            return format_html('<span style="color: orange; font-weight: bold;">Today</span>')
        elif obj.due_date < today and not obj.completed:
            days_overdue = (today - obj.due_date).days
            return format_html('<span style="color: red;">{} day(s) overdue</span>', days_overdue)
        else:
            return obj.due_date.strftime('%Y-%m-%d')
    due_date_display.short_description = 'Due Date'
    
    def has_attachment(self, obj):
        """Check if task has attachment"""
        return bool(obj.attachment)
    has_attachment.boolean = True
    has_attachment.short_description = 'Has Attachment'
    
    def attachment_preview(self, obj):
        """Show attachment info in admin"""
        if obj.attachment:
            return format_html('<a href="{}" target="_blank">Download {}</a> ({} KB)', 
                              obj.attachment.url, 
                              obj.attachment.name.split('/')[-1],
                              round(obj.attachment.size / 1024, 1))
        return "No attachment"
    attachment_preview.short_description = 'Attachment Preview'
    
    def overdue_status(self, obj):
        """Display overdue status"""
        if obj.is_overdue():
            return f"Overdue by {(timezone.now().date() - obj.due_date).days} days"
        return "Not overdue"
    overdue_status.short_description = 'Overdue Status'
    
    def days_until_due_display(self, obj):
        """Display days until due"""
        days = obj.days_until_due()
        if days is None:
            return "No due date"
        elif days < 0:
            return f"Overdue by {-days} days"
        elif days == 0:
            return "Due today"
        elif days == 1:
            return "Due tomorrow"
        else:
            return f"Due in {days} days"
    days_until_due_display.short_description = 'Due Status'
    
    # timezone is imported at module level

# Register models with custom admin classes
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Task, TaskAdmin)