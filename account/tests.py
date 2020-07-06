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
        usr3 = User.objects.create_user('test3@test.com', password='test')
        usr3.first_name = ""
        usr3.last_name = ""
        usr3.save()
        usrA = User.objects.create_superuser('test@admin.com', password='test')
        usrA.first_name = "Admin"
        usrA.last_name = "User"
        usrA.save()

    def test_get_full_name_with_user(self):
        """Test that user's full name is returned accurately"""
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_full_name(), 'Test1 User')
        self.assertEqual(user2.get_full_name(), 'Test2 User')
    def test_get_empty_name_with_user(self):
        """Test that user's full name is returned accurately"""
        user3 = User.objects.get(email="test3@test.com")
        self.assertEqual(user3.get_full_name(), 'test3@test.com')
    def test_get_short_name_with_user(self):
        """Test that user's email is returned accurately"""
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_short_name(), 'test1@test.com')
        self.assertEqual(user2.get_short_name(), 'test2@test.com')
    def test_admin_perm(self):
        """Test that an admin user has the proper permissions"""
        userA = User.objects.get(email="test@admin.com")
        self.assertEqual(userA.is_admin, True)
        self.assertEqual(userA.is_staff(), True)

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
        """Test that logging in with email logins in and redirects to profile page successfully."""
        form = {
            'email': 'test1@test.com',
            'password': 'test',
        }
        response = self.client.post('/login/', form, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/profile/')
    def test_failed_login_view_with_iam(self):
        """Test that logging in with incorrect credentials doesnt logins in and redirects to this login page."""
        form = {
            'email': 'test1@test.com',
            'password': 'test2',
        }
        response = self.client.post('/login/', form, follow=True)
        #messages = list(response.context['messages'])
        #self.assertEqual(len(messages), 1)
        #self.assertEqual(str(messages[0]), 'Invalid Credentials, Try again!')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/')
    def test_redirect_if_logged_in_already(self):
        """Test that viewing login page when already logged in redirects to profile page."""
        # login here
        form = {
            'email': 'test1@test.com',
            'password': 'test',
        }
        self.client.post('/login/', form, follow=True)
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/profile/')
    def test_redirect_if_logged_in_already_next(self):
        """Test that viewing login page when already logged in redirects to profile page."""
        # login here
        form = {
            'email': 'test1@test.com',
            'password': 'test',
        }
        self.client.post('/login/', form)
        response = self.client.get('/login/?next=/changepwd/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/changepwd/')
    def test_redirect_if_logged_out_next(self):
        """Test that viewing login page when already logged in redirects to profile page."""
        # login here
        response = self.client.get('/login/?next=/changepwd/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/login/')
        self.assertEqual(response.request['QUERY_STRING'], 'next=/changepwd/')
        

class UserSignUpViewTest(TestCase):
    """
    Class for testing user signup.
    """
    def setUp(self):
        """none"""
        pass
    def test_proper_get(self):
        response = self.client.get('/signup/')
        self.assertTemplateUsed(response, "account/signup.html")
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
    def test_proper_get(self):
        response = self.client.get('/changepwd/')
        self.assertTemplateUsed(response, "account/change_password.html")
    def test_pwd_change_with_post_request(self):
        """Test that updating the password of a logged in user is successful."""
        data = {
            "old_password": "test",
            "new_password1": "complexPWD123",
            "new_password2": "complexPWD123",
        }
        response = self.client.post('/changepwd/', data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/profile/')
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

class AWSCredViewTest(TestCase):
    """
    Class for testing user signup.
    """
    def setUp(self):
        """Create basic test users"""
        user = User.objects.create_user('test@test.com', password='test')
        user.first_name = "Test1"
        user.last_name = "User"
        user.save()
        aws_req = AWSRequest.objects.create(user=user)
        user2 = User.objects.create_user('test2@test.com', password='test')
        user2.first_name = "Test2"
        user2.last_name = "User"
        user2.save()
        
    def test_existing_cred_request(self):
        """Test that accessing the AWS Cred Request View with an existing request switches its state to pending and redirects to profile."""
        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
        }
        self.client.post('/login/', form)
        
        response = self.client.get('/aws_cred_request/')
        self.assertEqual(AWSRequest.objects.filter(user=User.objects.filter(email='test@test.com').first()).first().status, STATUS_PENDING)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/profile/')
    def test_no_cred_request(self):
        """Test that accessing the AWS Cred Request View without an existing request creates one and redirects to profile."""
        # login here
        form = {
            'email': 'test2@test.com',
            'password': 'test',
        }
        self.client.post('/login/', form)
        
        response = self.client.get('/aws_cred_request/')
        user = User.objects.filter(email='test@test.com').first()
        self.assertEqual(AWSRequest.objects.filter(user=user).first().user, user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/profile/')


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
