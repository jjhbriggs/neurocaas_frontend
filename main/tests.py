from django.test import TestCase

# Create your tests here.
from .models import Analysis, ConfigTemplate
from account.models import *
import os
from .utils import *
import yaml
from .views import flatten, unflatten

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

        group.analyses.add(analysis)

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
        group1.analyses.add(analysis1)

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
        group2.analyses.add(analysis2)

    def test_analysis_list_view(self):
        """Check that the the two analyses are displayed correctly."""
        response = self.client.get('/analyses/')
        self.assertQuerysetEqual(response.context['main_analyses'], ['<Analysis: Test Analysis1>'])
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

        group.analyses.add(analysis)

    def test_with_intro_view(self):
        """Checks that the proper analysis details are returned when visiting the analysis intro view."""
        response = self.client.get('/analysis/1')
        analysis = Analysis.objects.filter(analysis_name='Test Analysis').first()
        self.assertEqual(response.context['analysis'], analysis)
        self.assertEqual(response.context['iam'], None)

class JobListViewTest(TestCase):
    """Class for testing the job list view."""
    @classmethod
    def setUpClass(cls):
        cls.analysis = Analysis.objects.create(
            analysis_name="Test Analysis",
            result_prefix="job__cianalysispermastack_",
            bucket_name="cianalysispermastack",
            custom=False,
            short_description="Short Description",
            long_description="Long Description",
            paper_link="Paper Link",
            git_link="Github Link",
            bash_link="Bash Script Link",
            demo_link="Demo page link",
            signature="Signature"
        )
        cls.group = AnaGroup.objects.create(name="frontendtravisci")
        cls.group.analyses.add(cls.analysis)
        cls.group.save()
        cls.credential_response = build_credentials(cls.group, cls.analysis, testing=True)
    @classmethod
    def tearDownClass(cls):
        sts_teardown_all(testing=True)
        cls.group.delete()
        cls.analysis.delete()

    def setUp(self):
        """Setup user, group, IAM, and analysis. Login IAM."""
        self.user = User.objects.create_user('test@test.com', password='test')
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.group = self.group
        self.user.save()
        self.iam = IAM.objects.create(user=self.user,
                                      aws_user="jbriggs",
                                      aws_access_key='tbd',
                                      aws_secret_access_key='tbd',
                                      group=self.group)
        
        reassign_iam(self.iam, self.credential_response)
        self.group2 = AnaGroup.objects.create(name="NOACCESS")
        self.user2 = User.objects.create_user('test2@test.com', password='test')
        self.user2.first_name = "Test2"
        self.user2.last_name = "User2"
        self.user2.group = self.group2
        self.user2.save()
        self.iam2 = IAM.objects.create(user=self.user2,
                                      aws_user="jbriggs",
                                      aws_access_key='tbd',
                                      aws_secret_access_key='tbd',
                                      group=self.group2)
        
        self.group.analyses.add(self.analysis)        
    def test_job_list_view(self):
        """Check that history of user's analyses are displayed properly."""
        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
        response = self.client.get('/history/%s' % self.analysis.id)
        self.assertEqual(response.context['analysis'], self.analysis)
        self.assertEqual(response.context['iam'], self.iam)
        self.assertIsNotNone(response.context['job_list'])
    def test_no_perms_job_list_view(self):
        """Check that history of user's analyses is not displayed if the user doesn't have permission to access to the analysis."""
        # login here
        form = {
            'email': 'test2@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
        response = self.client.get('/history/%s' % self.analysis.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
