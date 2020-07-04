from django.test import TestCase
from django.urls import reverse
# Create your tests here.
from .models import *
from .managers import UserManager

class UserTestCase(TestCase):
    """
    Class for testing user information.
    """
    def setUp(self):
        """Create basic test users."""
        usr1 = User.objects.create_user('test1@test.com', password='test')
        usr1.first_name = "Test1"
        usr1.last_name = "User"
        usr1.save()
        usr2 = User.objects.create_user('test2@test.com', password='test')
        usr2.first_name = "Test2"
        usr2.last_name = "User"
        usr2.save()

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
        user = User.objects.create_user('test1@test.com', password='test')
        user.first_name = "Test1"
        user.last_name = "User"
        user.has_migrated_pwd = True
        user.save()
        
        #user = User.objects.create(email="test1@test.com", first_name="Test1", last_name="User")
        group = AnaGroup.objects.create(name="test group")
        IAM.objects.create(user=user,
                           aws_user="AWS user",
                           aws_access_key="AWS access key",
                           aws_secret_access_key="AWS secret key",
                           group=group)

    def test_login_view_with_iam(self):
        """Test that logging in with AWS credentials logins in and redirects to profile page successfully."""
        form = {
            'email': 'test1@test.com',
            'password': 'test',
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
            "password1": "complexPWD123",
            "password2": "complexPWD123",
            "next_url": "home"
        }
        response = self.client.post('/signup/', form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/home/')
    def test_unmatched_sign_up_view_with_post_request(self):
        """Test that signing up with unmatching passwords redirects to signup page successfully."""
        form_data = {
            "email": "test@test.com",
            "password1": "complexPWD123",
            "password2": "complexPWD1234",
            "next_url": "home"
        }
        response = self.client.post('/signup/', form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/signup/')
        
        
class ChangePWDTest(TestCase):
    """
    Class for testing the user profile page.
    """
    def setUp(self):
        """Create basic test user and associate it with a basic test IAM and group."""
        user = User.objects.create_user('test@test.com', password='test')
        user.first_name = "Test1"
        user.last_name = "User"
        user.save()
        group = AnaGroup.objects.create(name="test group")
        AWSRequest.objects.create(user=user)
        IAM.objects.create(user=user,
                           aws_user="AWS user",
                           aws_access_key="AWS access key",
                           aws_secret_access_key="AWS secret key",
                           group=group)

        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
        }
        self.client.post('/login/', form)

    def test_pwd_change_with_post_request(self):
        """Test that updating the password of a logged in user is successful."""
        data = {
            "old_password": "test",
            "new_password1": "complexPWD123",
            "new_password2": "complexPWD123",
        }
        response = self.client.post('/profile/', data)
        self.assertEqual(response.status_code, 302)
    def test_unmatched_pwd_change_with_post_request(self):
        """Test that updating the password with unmatched passwords of a logged in user fails."""
        data = {
            "old_password": "test",
            "new_password1": "complexPWD123",
            "new_password2": "complexPWD1234",
        }
        response = self.client.post('/changepwd/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/changepwd/')
    def test_incorrect_pwd_change_with_post_request(self):
        """Test that updating the password with unmatched passwords of a logged in user fails."""
        data = {
            "old_password": "test1",
            "new_password1": "complexPWD123",
            "new_password2": "complexPWD123",
        }
        response = self.client.post('/changepwd/', data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/changepwd/')

class ProfileViewTest(TestCase):
    """
    Class for testing the user profile page.
    """
    def setUp(self):
        """Create basic test user and associate it with a basic test IAM and group."""
        user = User.objects.create_user('test@test.com', password='test')
        user.first_name = "Test1"
        user.last_name = "User"
        user.save()
        group = AnaGroup.objects.create(name="test group")
        AWSRequest.objects.create(user=user)
        IAM.objects.create(user=user,
                           aws_user="AWS user",
                           aws_access_key="AWS access key",
                           aws_secret_access_key="AWS secret key",
                           group=group)

        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
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
