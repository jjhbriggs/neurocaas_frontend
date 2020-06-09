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


class AnalysisListViewTest(TestCase):
    def setUp(self):
        group1 = AnaGroup.objects.create(name="test group1")
        group2 = AnaGroup.objects.create(name="test group2")
        analysis1 = Analysis.objects.create(
            analysis_name="Test Analysis1",
            result_prefix="test_prefix1",
            bucket_name="Test bucket1",
            custom=False,
            short_description="Short Description1",
            long_description="Long Description1",
            paper_link="Paper Link1",
            git_link="Github Link1",
            bash_link="Bash Script Link1",
            demo_link="Demo page link1",
            signature="Signature1"
        )
        analysis1.groups.add(group1)

        analysis2 = Analysis.objects.create(
            analysis_name="Test Analysis2",
            result_prefix="test_prefix2",
            bucket_name="Test bucket2",
            custom=True,
            short_description="Short Description2",
            long_description="Long Description2",
            paper_link="Paper Link2",
            git_link="Github Link2",
            bash_link="Bash Script Link2",
            demo_link="Demo page link2",
            signature="Signature2"
        )
        analysis2.groups.add(group2)

    def test_analysis_list_view(self):
        response = self.client.get('/analyses/')
        self.assertQuerysetEqual(response.context['main_analyses'], ['<Analysis: Test Analysis1>'])
        self.assertQuerysetEqual(response.context['custom_analyses'], ['<Analysis: Test Analysis2>'])
