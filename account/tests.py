from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from .models import *


class UserTestCase(TestCase):
    """
    Class for testing user information.
    """
    def setUp(self):
        """Create basic test users."""
        User.objects.create(email="test1@test.com", first_name="Test1", last_name="User")
        User.objects.create(email="test2@test.com", first_name="Test2", last_name="User")

    def test_get_full_name_with_user(self):
        """Test that user's full name is returned accurately"""
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_full_name(), 'Test1 User')
        self.assertEqual(user2.get_full_name(), 'Test2 User')

    def test_get_short_name_with_user(self):
        """Test that user's email is returned accurately"""
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_short_name(), 'test1@test.com')
        self.assertEqual(user2.get_short_name(), 'test2@test.com')


class UserLoginViewTest(TestCase):
    """
    Class for testing user login.
    """
    def setUp(self):
        """Create basic test user and associate it with a basic test IAM and group."""
        user = User.objects.create(email="test1@test.com", first_name="Test1", last_name="User")
        group = AnaGroup.objects.create(name="test group")
        IAM.objects.create(user=user,
                           aws_user="AWS user",
                           aws_access_key="AWS access key",
                           aws_secret_access_key="AWS secret key",
                           group=group)

    def test_login_view_with_iam(self):
        """Test that logging in with AWS credentials logins in and redirects to profile page successfully."""
        form = {
            'aws_access_key': 'AWS access key',
            'aws_secret_access_key': 'AWS secret key',
        }
        response = self.client.post('/login/', form, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/profile/')


class UserSignUpViewTest(TestCase):
    """
    Class for testing user signup.
    """
    def setUp(self):
        """none"""
        pass

    def test_sign_up_view_with_post_request(self):
        """Test that signing up with email signs up and redirects to home page successfully."""
        form_data = {
            "email": "test@test.com",
            "next_url": "home"
        }
        response = self.client.post('/signup/', form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/home/')


class ProfileViewTest(TestCase):
    """
    Class for testing the user profile page.
    """
    def setUp(self):
        """Create basic test user and associate it with a basic test IAM and group."""
        user = User.objects.create(email="test@test.com", first_name="Test1", last_name="User")
        group = AnaGroup.objects.create(name="test group")
        AWSRequest.objects.create(user=user)
        IAM.objects.create(user=user,
                           aws_user="AWS user",
                           aws_access_key="AWS access key",
                           aws_secret_access_key="AWS secret key",
                           group=group)

        # login here
        form = {
            'aws_access_key': 'AWS access key',
            'aws_secret_access_key': 'AWS secret key',
        }
        self.client.post('/login/', form)

    def test_profile_view_with_get_request(self):
        """Test that checking the profile view of a logged in user displays the user's email, name, and IAM username."""
        response = self.client.get('/profile/')
        self.assertEqual(response.context['user'].email, "test@test.com")
        self.assertEqual(response.context['aws_req'].user.get_full_name(), "Test1 User")
        self.assertEqual(response.context['iam'].aws_user, "AWS user")

    def test_profile_view_with_post_request(self):
        """Test that updating the profile view of a logged in user is successful."""
        data = {
            "first_name": "Test2",
            "last_name": "User2"
        }
        response = self.client.post('/profile/', data)
        self.assertEqual(response.status_code, 302)
