from django.test import TestCase

# Create your tests here.
from .models import *


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(email="test1@test.com", first_name="Test1", last_name="User")
        User.objects.create(email="test2@test.com", first_name="Test2", last_name="User")

    def test_get_full_name_with_user(self):
        """ User's full name check """
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_full_name(), 'Test1 User')
        self.assertEqual(user2.get_full_name(), 'Test2 User')

    def test_get_short_name_with_user(self):
        """ User's email as short name """
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_short_name(), 'test1@test.com')
        self.assertEqual(user2.get_short_name(), 'test2@test.com')


class UserLoginViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(email="test1@test.com", first_name="Test1", last_name="User")
        group = AnaGroup.objects.create(name="test group")
        IAM.objects.create(user=user,
                           aws_user="AWS user",
                           aws_access_key="AWS access key",
                           aws_secret_access_key="AWS secret key",
                           group=group)

    def test_login_view_with_iam(self):
        """ Login Test with AWS credentials """
        form = {
            'aws_access_key': 'AWS access key',
            'aws_secret_access_key': 'AWS secret key',
        }
        response = self.client.post('/signup/', form)
        self.assertEqual(response.status_code, 200)
