from django.test import TestCase

# Create your tests here.
from .models import Analysis
from account.models import *


class AnalysisTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(email="test1@test.com", first_name="Test1", last_name="User")
        group = AnaGroup.objects.create(name="test group")
        self.iam = IAM.objects.create(user=user,
                                      aws_user="AWS user",
                                      aws_access_key="AWS access key",
                                      aws_secret_access_key="AWS secret key",
                                      group=group)

        # Analysis.objects.create(
        #     analysis_name="Test Analysis",
        #     result_prefix="test_prefix",
        #     bucket_name="Test bucket",
        #     custom=True,
        #     groups=group,
        #     short_description="Short Description",
        #     long_description="Long Description",
        #     paper_link="Paper Link",
        #     git_link="Github Link",
        #     bash_link="Bash Script Link",
        #     demo_link="Demo page link",
        #     signature="Signature"
        # )

    def test_check_iam_with_analysis(self):
        """ User's full name check """

        user1 = User.objects.get(email="test1@test.com")
        user2 = User.objects.get(email="test2@test.com")
        self.assertEqual(user1.get_full_name(), 'Test1 User')
        self.assertEqual(user2.get_full_name(), 'Test User')
