from django.test import TestCase
from django.contrib.auth.models import User
from to_do_app.forms import ProfileForm, RegistrationForm
from datetime import date


class ProfileFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')

    def test_valid_profile_form(self):
        form = ProfileForm(data={
            'first_name': 'John',
            'last_name': 'Dave',
            'title': 'Developer',
            'bio': 'Hello world',
            'location': 'Johannesburg',
            'birth_date': date(1990, 1, 1),
            'phone': '123456789',
            'website': 'https://example.com',
            'email_notifications': True,
        })
        self.assertTrue(form.is_valid())

    def test_invalid_profile_form_bad_url(self):
        form = ProfileForm(data={
            'first_name': 'John',
            'last_name': 'Dave',
            'website': 'not-a-url',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

    def test_profile_form_labels_and_help_texts(self):
        form = ProfileForm()
        self.assertEqual(form.fields['first_name'].label, 'First Name')
        self.assertEqual(form.fields['title'].help_text, 'Your professional title or occupation')
        self.assertEqual(form.fields['bio'].help_text, 'Tell us a little about yourself')
        self.assertEqual(form.fields['phone'].help_text, 'Optional')

    def test_profile_form_widget_classes(self):
        form = ProfileForm()
        # All fields except email_notifications should have 'form-control'
        for name, field in form.fields.items():
            if name == 'email_notifications':
                self.assertEqual(field.widget.attrs.get('class'), 'form-check-input')
            else:
                self.assertEqual(field.widget.attrs.get('class'), 'form-control')


class RegistrationFormTests(TestCase):
    def test_valid_registration_form(self):
        form = RegistrationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_registration_form_mismatched_passwords(self):
        form = RegistrationForm(data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'StrongPass123!',
            'password2': 'MismatchPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_registration_form_missing_email(self):
        form = RegistrationForm(data={
            'username': 'newuser',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_registration_form_widget_placeholders(self):
        form = RegistrationForm()
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], 'Choose a username')
        self.assertEqual(form.fields['password1'].widget.attrs['placeholder'], 'Create a password')
        self.assertEqual(form.fields['password2'].widget.attrs['placeholder'], 'Confirm your password')

    def test_registration_form_help_text(self):
        form = RegistrationForm()
        # password1 help text should be set by password_validation
        self.assertTrue(len(form.fields['password1'].help_text) > 0)

