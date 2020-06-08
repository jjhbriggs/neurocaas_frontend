from django.test import TestCase

# Create your tests here.
from .models import Analysis
from account.models import *


class AnalysisTestCase(TestCase):
    def setUp(self):
        User.objects.create(email="test1@test.com", first_name="Test1", last_name="User")
        User.objects.create(email="test2@test.com", first_name="Test2", last_name="User")

    def test_get_full_name_with_user(self):
        """ User's full name check """
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_full_name(), 'Test1 User')
        self.assertEqual(user2.get_full_name(), 'Test User')

    def test_get_short_name_with_user(self):
        """ User's email as short name """
        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_short_name(), 'Test1 User')
        self.assertEqual(user2.get_short_name(), 'test1@test.com')

