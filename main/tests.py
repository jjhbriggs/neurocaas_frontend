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

        analysis = Analysis.objects.create(
            analysis_name="Test Analysis",
            result_prefix="test_prefix",
            bucket_name="Test bucket",
            custom=True,
            short_description="Short Description",
            long_description="Long Description",
            paper_link="Paper Link",
            git_link="Github Link",
            bash_link="Bash Script Link",
            demo_link="Demo page link",
            signature="Signature"
        )

        analysis.groups.add(group)

    def test_check_iam_with_analysis(self):
        """ User's full name check """

        analysis = Analysis.objects.get(bucket_name='Test bucket')
        iam = IAM.objects.get(aws_user='AWS user')
        self.assertIs(analysis.check_iam(iam), True)
