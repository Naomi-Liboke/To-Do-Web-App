from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import password_validation

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'title', 
            'bio', 'location', 'birth_date', 
            'phone', 'website', 'avatar', 
            'email_notifications'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter your first name',
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter your last name',
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g., Software Developer, Student, etc.',
                'class': 'form-control'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'class': 'form-control'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Your location',
                'class': 'form-control'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone number',
                'class': 'form-control'
            }),
            'website': forms.URLInput(attrs={
                'placeholder': 'https://yourwebsite.com',
                'class': 'form-control'
            }),
            'email_notifications': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set custom labels
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['title'].label = 'Title / Profession'
        self.fields['bio'].label = 'Bio'
        self.fields['location'].label = 'Location'
        self.fields['birth_date'].label = 'Birth Date'
        self.fields['phone'].label = 'Phone Number'
        self.fields['website'].label = 'Website'
        self.fields['avatar'].label = 'Profile Picture'
        self.fields['email_notifications'].label = 'Receive email notifications'
        
        # Add help text
        self.fields['title'].help_text = 'Your professional title or occupation'
        self.fields['bio'].help_text = 'Tell us a little about yourself'
        self.fields['phone'].help_text = 'Optional'
        self.fields['website'].help_text = 'Optional'
        self.fields['birth_date'].help_text = 'Optional'
        
        # Ensure all fields have form-control class except checkbox
        for field_name, field in self.fields.items():
            if field_name != 'email_notifications':
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control'
    }))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent classes/placeholders
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

        # Use Django's configured password validators help text (HTML)
        try:
            self.fields['password1'].help_text = password_validation.password_validators_help_text_html()
        except Exception:
            # Fallback to plain text list if html helper is unavailable
            self.fields['password1'].help_text = '\n'.join(password_validation.password_validators_help_texts())