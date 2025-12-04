from django.test import TestCase
from django.contrib.auth.models import User
from to_do_app.models import Profile
from django.core.management import call_command
from io import StringIO


class CreateProfilesCommandTests(TestCase):
    def test_creates_profiles_for_users_without_profiles(self):
        # Create users without profiles
        user1 = User.objects.create_user(username='user1', password='pass')
        user2 = User.objects.create_user(username='user2', password='pass')

        # Delete their auto-created profiles to simulate missing profiles
        Profile.objects.filter(user=user1).delete()
        Profile.objects.filter(user=user2).delete()

        # Run the command by instantiating the Command class directly
        out = StringIO()
        from to_do_app.create_profiles import Command
        cmd = Command()
        cmd.stdout = out
        cmd.handle()

        # Verify profiles were created
        self.assertTrue(Profile.objects.filter(user=user1).exists())
        self.assertTrue(Profile.objects.filter(user=user2).exists())

        # Verify output contains success messages
        output = out.getvalue()
        self.assertIn('Created profile for user1', output)
        self.assertIn('Created profile for user2', output)
        self.assertIn('Created profiles for 2 users', output)

    def test_no_profiles_created_if_all_exist(self):
        # Create a user with an existing profile
        user = User.objects.create_user(username='existing', password='pass')
        # Profile is auto-created by signal

        # Run the command by instantiating the Command class directly
        out = StringIO()
        from to_do_app.create_profiles import Command
        cmd = Command()
        cmd.stdout = out
        cmd.handle()

        # Verify no new profiles created
        self.assertEqual(Profile.objects.filter(user=user).count(), 1)

        # Output should indicate 0 users processed
        output = out.getvalue()
        self.assertIn('Created profiles for 0 users', output)
