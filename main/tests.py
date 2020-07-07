from django.test import TestCase

# Create your tests here.
from .models import Analysis
from account.models import *


class AnalysisTestCase(TestCase):
    """Class for testing IAM connected to analyses."""
    def setUp(self):
        """Setup user, group, IAM, and analysis"""
        user = User.objects.create_user('test1@test.com', password='test')
        user.first_name = "Test1"
        user.last_name = "User"
        user.save()
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
        """Test the current IAM is the same which is associated with the analysis request."""

        analysis = Analysis.objects.get(bucket_name='Test bucket')
        iam = IAM.objects.get(aws_user='AWS user')
        self.assertIs(analysis.check_iam(iam), True)


class AnalysisListViewTest(TestCase):
    """Class for testing the list view of analyses."""
    def setUp(self):
        """Setup two groups and analyses"""
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
        """Check that the the two analyses are displayed correctly."""
        response = self.client.get('/analyses/')
        #print(response.context)
        #print("hi")
        self.assertQuerysetEqual(response.context['main_analyses'], ['<Analysis: Test Analysis1>'])
        #print(response.context['main_analyses'])
        self.assertQuerysetEqual(response.context['custom_analyses'], ['<Analysis: Test Analysis2>'])
        self.assertEqual(response.context['iam'], None)


class AnalysisIntroViewTest(TestCase):
    """Class for testing analysis intro view."""
    def setUp(self):
        """Setup user, group, IAM, and analysis"""
        user = User.objects.create_user('test1@test.com', password='test')
        user.first_name = "Test1"
        user.last_name = "User"
        user.save()
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

    def test_with_intro_view(self):
        """Checks that the proper analysis details are returned when visiting the analysis intro view."""
        response = self.client.get('/analysis/1')
        analysis = Analysis.objects.filter(analysis_name='Test Analysis').first()
        self.assertEqual(response.context['analysis'], analysis)
        self.assertEqual(response.context['iam'], None)


# class JobListViewTest(TestCase):
#     """Class for testing the job list view."""
#     def setUp(self):
#         """Setup user, group, IAM, and analysis. Login IAM."""
#         self.user = User.objects.create_user('test1@test.com', password='test')
#         self.user.first_name = "Johannes"
#         self.user.last_name = "Fourie"
#         self.user.save()
#         #self.user = User.objects.create(email="test1@test.com", first_name="Johannes", last_name="Fourie")
#         self.group = AnaGroup.objects.create(name="reviewers")
#         self.iam = IAM.objects.create(user=self.user,
#                                       aws_user="johannesus-east-1",
#                                       aws_access_key="AKIA2YSWAZCCRK2H3SHJ",
#                                       aws_secret_access_key="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",
#                                       group=self.group)
# 
#         self.analysis = Analysis.objects.create(
#             analysis_name="Emergent Property Inference (Bittner et al. 2019)",
#             result_prefix="job__epi-ncap-web_",
#             bucket_name="epi-ncap-web",
#             custom=False,
#             short_description="Short Description",
#             long_description="Long Description",
#             paper_link="Paper Link",
#             git_link="Github Link",
#             bash_link="Bash Script Link",
#             demo_link="Demo page link",
#             signature="Signature"
#         )
# 
#         self.analysis.groups.add(self.group)
# 
#         # login here
#         form = {
#             'email': 'test1@test.com',
#             'password': 'test',
#         }
#         #form = {
#         #    'aws_access_key': 'AKIA2YSWAZCCRK2H3SHJ',
#         #    'aws_secret_access_key': '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',
#         #}
#         self.client.post('/login/', form)
# 
#     def test_job_list_view(self):
#         """Check that history of user's analyses are displayed properly."""
#         response = self.client.get('/history/%s' % self.analysis.id)
#         self.assertEqual(response.context['analysis'], self.analysis)
#         self.assertEqual(response.context['iam'], self.iam)
