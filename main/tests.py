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
    def setUp(self):
        """Setup user, group, IAM, and analysis. Login IAM."""
        self.analysis = Analysis.objects.create(
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

        
        self.group = AnaGroup.objects.create(name="frontendtravisci")
        self.group.analyses.add(self.analysis)
        self.group.save()
        
        #: User with unfixed creds and access
        self.user = User.objects.create_user('test@test.com', password='test')
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.group = self.group
        self.user.save()
        self.iam = IAM.objects.create(user=self.user,
                                    aws_access_key='tbd',
                                    aws_secret_access_key='tbd',
                                    group=self.group)
        reassign_iam(self.iam, build_credentials(self.group, self.analysis, testing=True))

        #: User with unfixed creds and no access
        self.group2 = AnaGroup.objects.create(name="NOACCESS")
        self.user2 = User.objects.create_user('test2@test.com', password='test')
        self.user2.first_name = "Test2"
        self.user2.last_name = "User2"
        self.user2.group = self.group2
        self.user2.save()
        self.iam2 = IAM.objects.create(user=self.user2,
                                    aws_access_key='tbd',
                                    aws_secret_access_key='tbd',
                                    group=self.group2)

        #: User with fixed creds and access
        self.usera = User.objects.create_user('testa@test.com', password='test')
        self.usera.first_name = "Test"
        self.usera.last_name = "User"
        self.usera.group = self.group
        self.usera.save()
        self.iama = IAM.objects.create(user=self.usera,
                                    aws_user="jbriggs",
                                    aws_access_key=os.environ.get('AWS_ACCESS_KEY'),
                                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                                    fixed_creds=True,
                                    group=self.group)

        #: User with fixed creds and no access

        self.user2a = User.objects.create_user('test2a@test.com', password='test')
        self.user2a.first_name = "Test2"
        self.user2a.last_name = "User2"
        self.user2a.group = self.group2
        self.user2a.save()
        self.iam2a = IAM.objects.create(user=self.user2a,
                                    aws_user="invalid",
                                    aws_access_key='tbd',
                                    aws_secret_access_key='tbd',
                                    fixed_creds=True,
                                    group=self.group2)

    def test_job_list_view_unfixed(self):
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
        sts_teardown_all(testing=True)
    def test_job_list_view_fixed(self):
        """Check that history of user's analyses are displayed properly."""
        # login here
        form = {
            'email': 'testa@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
        response = self.client.get('/history/%s' % self.analysis.id)
        self.assertEqual(response.context['analysis'], self.analysis)
        self.assertEqual(response.context['iam'], self.iama)
        self.assertIsNotNone(response.context['job_list'])
    def test_no_perms_job_list_view_unfixed(self):
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
        sts_teardown_all(testing=True)
    def test_no_perms_job_list_view_fixed(self):
        """Check that history of user's analyses is not displayed if the user doesn't have permission to access to the analysis."""
        # login here
        form = {
            'email': 'test2a@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
        response = self.client.get('/history/%s' % self.analysis.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')

# class JobDetailViewTest(TestCase):
#     """Class for testing the job detail view."""
#     #if os.environ.get('CI') is None or not os.environ.get('CI'):
#     @classmethod
#     def setUpClass(cls):
#         cls.analysis = Analysis.objects.create(
#             analysis_name="Test Analysis",
#             result_prefix="job__cianalysispermastack_",
#             bucket_name="cianalysispermastack",
#             custom=False,
#             short_description="Short Description",
#             long_description="Long Description",
#             paper_link="Paper Link",
#             git_link="Github Link",
#             bash_link="Bash Script Link",
#             demo_link="Demo page link",
#             signature="Signature"
#         )
#         cls.group = AnaGroup.objects.create(name="frontendtravisci")
#         cls.group.analyses.add(cls.analysis)
#         cls.group.save()
#         cls.credential_response = build_credentials(cls.group, cls.analysis, testing=True)
#     @classmethod
#     def tearDownClass(cls):
#         sts_teardown_all(testing=True)
#         cls.group.delete()
#         cls.analysis.delete()

#     def setUp(self):
#         """Setup user, group, IAM, and analysis. Login IAM."""
#         self.user = User.objects.create_user('test@test.com', password='test')
#         self.user.first_name = "Test"
#         self.user.last_name = "User"
#         self.user.group = self.group
#         self.user.save()
#         self.iam = IAM.objects.create(user=self.user,
#                                     aws_user="jbriggs",
#                                     aws_access_key='tbd',
#                                     aws_secret_access_key='tbd',
#                                     group=self.group)
                                    
#         reassign_iam(self.iam, self.credential_response)

#         self.group2 = AnaGroup.objects.create(name="NOACCESS")
#         self.user2 = User.objects.create_user('test2@test.com', password='test')
#         self.user2.first_name = "Test2"
#         self.user2.last_name = "User2"
#         self.user2.group = self.group2
#         self.user2.save()
#         self.iam2 = IAM.objects.create(user=self.user2,
#                                     aws_user="jbriggs",
#                                     aws_access_key='tbd',
#                                     aws_secret_access_key='tbd',
#                                     group=self.group2) 
#         res_folder = '%s/results' % self.group

#         job_list = get_job_list(iam=self.iam, bucket=self.analysis.bucket_name, folder=res_folder)
#         self.job_id = job_list[0]['name']
#     def test_job_detail_view(self):
#         """Check that detail of a user's previous analysis are displayed properly."""
#         form = {
#             'email': 'test@test.com',
#             'password': 'test',
#         }
#         r = self.client.post('/login/', form)
        
#         response = self.client.get('/history/' + str(self.analysis.id) + '/' + self.job_id)
        
#         self.assertEqual(response.context['analysis'], self.analysis)
#         self.assertEqual(response.context['iam'], self.iam)
#         self.assertIsNotNone(response.context['job_detail'])
#     def test_no_perms_job_list_view(self):
#         """Check that detail of a user's previous analysis is not displayed if the user doesn't have permission to access to the analysis."""
#         form = {
#             'email': 'test2@test.com',
#             'password': 'test',
#         }
#         r = self.client.post('/login/', form)
#         res_folder = '%s/results' % self.group2

#         job_list2 = get_job_list(iam=self.iam2, bucket=self.analysis.bucket_name, folder=res_folder)
#         response = self.client.get('/history/' + str(self.analysis.id) + '/' + self.job_id)
        
#         self.assertEqual(len(job_list2),0)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response['Location'], '/')
    
class UserFilesViewTest(TestCase):
    """Class for testing the user files view."""
    
    def setUp(self):
        """Setup user, group, IAM, and analysis. Login IAM."""
        
        self.user = User.objects.create_user('test@test.com', password='test')
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.save()
        self.group = AnaGroup.objects.create(name="frontendtravisci")
        self.iam = IAM.objects.create(user=self.user,
                                      aws_user="jbriggs",
                                      aws_access_key=os.environ.get('AWS_ACCESS_KEY'),
                                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                                      group=self.group)
        self.analysis = Analysis.objects.create(
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
        self.group.analyses.add(self.analysis)
        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
        
    def test_get_user_files(self):
        """Check that detail of a user's previous analysis are displayed properly."""
        
        response = self.client.get('/user_files/%s' % self.analysis.id)
        data = response.json()

        self.assertEqual(data['status'], 200)
        self.assertIsNotNone(data['data_sets'])
        self.assertIsNotNone(data['configs'])
        
class ProcessViewTest(TestCase):
    """Class for testing the process view."""
    #: Note when this is loaded it makes 'non-testing' sts roles, but its fine as they will be eventually by system use.
    #: Alternative would involve passing testing variables to the view or something similarly unnessecary 
    
    def setUp(self):
        """Setup user, group, IAM, and analysis. Login IAM."""
        
        self.group = AnaGroup.objects.create(name="frontendtravisci")
        self.user = User.objects.create_user('test@test.com', password='test')
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.group = self.group
        self.user.save()
        
        self.iam = IAM.objects.create(user=self.user,
                                      aws_user="jbriggs",
                                      aws_access_key=os.environ.get('AWS_ACCESS_KEY'),
                                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                                      fixed_creds=True,
                                      group=self.group)
        self.analysis = Analysis.objects.create(
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
        self.group.analyses.add(self.analysis)
        self.analysis2 = Analysis.objects.create(
            analysis_name="Test Analaysis (No perms)",
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
        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
        
    def test_get_process_view(self):
        """Check that getting the process information displays properly."""
        
        response = self.client.get('/process/%s' % self.analysis.id)
        self.assertNotEqual(response.context, None)
        self.assertEqual(response.context['analysis'], self.analysis)
        self.assertEqual(response.context['iam'], self.iam)
        self.assertIsNotNone(response.context['id1'])
        self.assertIsNotNone(response.context['id2'])
        self.assertEqual(response.context["data_set_dir"], "%s/inputs" % self.iam.group.name)
        self.assertEqual(response.context["config_dir"], "%s/configs" % self.iam.group.name)
        self.assertEqual(response.context["bucket"], self.analysis.bucket_name)
        
    def test_no_perms_get_process(self):
        """Check that getting the process information does not display if the user does not have permissions for the analysis."""
        
        response = self.client.get('/process/%s' % self.analysis2.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/')
        
    def test_post_to_process_view(self):
        """Check that posting file names returns the proper json response."""

        form = {
            'config_file': 'sample_file_name.txt',
            "data_set_files[]": ["sample_file_name_2.txt", "sample_file_name_3.txt"],
        }
        response = self.client.post('/process/%s' % self.analysis.id, form, follow=True)
        
        data = response.json()
        
        #add new result to a file which flags it for removal 
        upload_data = "frontendtravisci/results/job__cianalysispermastack_" + str(data['timestamp']) + "/\n"
        # Method 1: Object.put()
        s3 = boto3.resource('s3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
        object = s3.Object('cianalysispermastack', 'frontendtravisci/results/prefixes_for_delete.txt')
        content = object.get()['Body'].read().decode('utf-8') 
        object.put(Body=content + upload_data)
        '''if data['timestamp'] != "":
            try:
                print(os.path.join(os.path.dirname(os.path.dirname(__file__)), "prefixes_for_delete.txt"))
                with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "prefixes_for_delete.txt"), "a") as f:
                    f.write("frontendtravisci/results/job__cianalysispermastack_" + str(data['timestamp']) + "/\n")
            except EnvironmentError:
                print ('There was an error flagging data for removal')'''
        self.assertEqual(data['status'], True)
        self.assertIsNotNone(data['timestamp'])
        self.assertIsNotNone(data['data_set_files'])
        self.assertIsNotNone(data['config_file'])
        
class ResultViewTest(TestCase):
    """Class for testing the result view."""
    #: See ProcessViewTest note
    def setUp(self):
        """Setup user, group, IAM, and analysis. Login IAM."""
        
        self.user = User.objects.create_user('test@test.com', password='test')
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.save()
        self.group = AnaGroup.objects.create(name="frontendtravisci")
        self.iam = IAM.objects.create(user=self.user,
                                      aws_user="jbriggs",
                                      aws_access_key=os.environ.get('AWS_ACCESS_KEY'),
                                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                                      group=self.group)
        self.analysis = Analysis.objects.create(
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
        self.group.analyses.add(self.analysis)
        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
        
    def test_get_results(self):
        """Check that detail of a user's previous analysis are displayed properly."""

        #the timestamp used here is arbitrary, it works as long as there is a corresponding file in s3.
        response = self.client.get('/results/%s' % self.analysis.id,{'timestamp': str(1)}) 
        data = response.json()

        self.assertEqual(data['status'], True)
        self.assertNotEqual(data['cert_file'], "")
    def test_post_results(self):
        """Check that is able to retrieve files from results and logs folder on s3 and determine if analysis was finished or not."""

        #the timestamp used here is arbitrary, it works as long as there is a corresponding file in s3.
        response = self.client.post('/results/%s' % self.analysis.id,{'timestamp': str(1)}, follow=True) 
        data = response.json()

        self.assertEqual(data['status'], 200)
        self.assertNotEqual(data["result_links"], "")
        self.assertEqual(data["end"], True)

# class ConfigViewTest(TestCase):
#     """Class for testing the process view."""
#     @classmethod
#     def setUpClass(cls):
#         cls.configTemplate = ConfigTemplate.objects.create(
#             config_name="Test Config",
#             orig_yaml="__sample_field__: 'sample'",
#         )
#         cls.analysis = Analysis.objects.create(
#             analysis_name="Test Analysis",
#             result_prefix="job__cianalysispermastack_",
#             bucket_name="cianalysispermastack",
#             custom=False,
#             config_template=cls.configTemplate,
#             short_description="Short Description",
#             long_description="Long Description",
#             paper_link="Paper Link",
#             git_link="Github Link",
#             bash_link="Bash Script Link",
#             demo_link="Demo page link",
#             signature="Signature"
#         )
#         cls.group = AnaGroup.objects.create(name="frontendtravisci")
#         cls.group.analyses.add(cls.analysis)
#         cls.group.save()
        
#         #cls.credential_response = build_credentials(cls.group, cls.analysis, testing=True)
#     @classmethod
#     def tearDownClass(cls):
#         sts_teardown_all(testing=True)
#         cls.group.delete()
#         cls.analysis.delete()
#         cls.configTemplate.delete()
#     def setUp(self):
#         """Setup user, group, IAM, and analysis. Login IAM."""
#         self.user = User.objects.create_user('test@test.com', password='test')
#         self.user.first_name = "Test"
#         self.user.last_name = "User"
#         self.user.group = self.group
#         self.user.save()
#         self.iam = IAM.objects.create(user=self.user,
#                                     aws_user="jbriggs",
#                                     aws_access_key='tbd',
#                                     aws_secret_access_key='tbd',
#                                     group=self.group)
#         #reassign_iam(self.iam, self.credential_response)

#         self.group2 = AnaGroup.objects.create(name="NOACCESS")
#         self.user2 = User.objects.create_user('test2@test.com', password='test')
#         self.user2.first_name = "Test2"
#         self.user2.last_name = "User2"
#         self.user2.group = self.group2
#         self.user2.save()
#         self.iam2 = IAM.objects.create(user=self.user2,
#                                     aws_user="jbriggs",
#                                     aws_access_key='tbd',
#                                     aws_secret_access_key='tbd',
#                                     group=self.group2) 
        
#     def test_get_config_view(self):
#         """Check that the config information displays properly."""
#         form = {
#             'email': 'test@test.com',
#             'password': 'test',
#         }
#         r = self.client.post('/login/', form)
        
#         response = self.client.get('/config/%s' % self.analysis.id)
#         self.assertEqual(response.context['analysis'], self.analysis)
#         self.assertEqual(response.context['iam'], self.iam)
#         self.assertIsNotNone(response.context['id1'])
#         self.assertIsNotNone(response.context['id2'])
#         self.assertEqual(response.context["logged_in"], True)
#         self.assertEqual(response.context["user"], self.user)
#         self.assertEqual(response.context["config_sample"], "__sample_field__: 'sample'")
#         self.assertIsNotNone(response.context['data'])
        
#     def test_no_perms_get_config(self):
#         """Check that getting the config information does not display if the user does not have permissions for the analysis."""
#         form = {
#             'email': 'test2@test.com',
#             'password': 'test',
#         }
#         r = self.client.post('/login/', form)
        
#         response = self.client.get('/config/%s' % self.analysis.id)
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response['Location'], '/')
        
#     def test_post_fail_to_config_view(self):
#         """Check that posting file fails."""
#         form = {
#             'email': 'test@test.com',
#             'password': 'test',
#         }
#         r = self.client.post('/login/', form)

#         response = self.client.post('/config/%s' % self.analysis.id, {'fail':'fail'}, follow=True)
#         self.assertContains(response, "Config Error: ")
#     def test_flatten_and_unflatten(self):
#         field_data = yaml.safe_load(self.analysis.config_template.orig_yaml)
#         self.assertEqual(unflatten(flatten(field_data)), field_data)

class ExtraUtilsTest(TestCase):
    """Class for extra tests on utils.py."""

    def setUp(self):
        """Setup user, group, IAM, and analysis. Login IAM."""
        
        self.user = User.objects.create_user('test@test.com', password='test')
        self.user.first_name = "Test"
        self.user.last_name = "User"
        self.user.save()
        self.group = AnaGroup.objects.create(name="frontendtravisci")
        self.iam = IAM.objects.create(user=self.user,
                                      aws_user="jbriggs",
                                      aws_access_key=os.environ.get('AWS_ACCESS_KEY'),
                                      aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                                      group=self.group)
        self.analysis = Analysis.objects.create(
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
        self.group.analyses.add(self.analysis)
        # login here
        form = {
            'email': 'test@test.com',
            'password': 'test',
        }
        r = self.client.post('/login/', form)
    def test_convert_size(self):
        self.assertEqual(convert_size(1024), "1024 B")
        self.assertEqual(convert_size(2048), "2.0 KB")
        self.assertEqual(convert_size(2097152), "2.0 MB")
        self.assertEqual(convert_size(2147483648), "2.0 GB")
    def test_get_name_only(self):
        self.assertEqual(get_name_only("path/to/folder"), "folder")
    def test_generate_folder(self):
        self.assertEqual("static/downloads" in generate_folder(), True)
    def test_up_and_down_file_to_s3(self):
        res_key = '%s/temp/test.txt' % self.group
        f = open("test.txt", "a")
        f.write("Test content")
        f.close()
        ret = upload_file_to_s3(iam=self.iam, bucket=self.analysis.bucket_name, key=res_key, file_path="test.txt")
        key = "temp/test.txt"
        file_key = "%s/%s" % (self.group.name, key)
        folder = generate_folder()
        ret = download_file_from_s3(iam=self.iam, bucket=self.analysis.bucket_name, key=file_key, folder=folder)
        self.assertIsNotNone(ret)
        res_folder = '%s/temp' % self.group
        ret = download_directory_from_s3(iam=self.iam, bucket=self.analysis.bucket_name, folder=res_folder)
        self.assertIsNotNone(ret)
    def test_get_last_modified_timestamp_err(self):
        ret = get_last_modified_timestamp(iam=self.iam, bucket=self.analysis.bucket_name, key="THROW_ERROR")
        self.assertEqual(ret, 0)
    def test_get_file_content_err(self):
        ret = get_file_content(iam=self.iam, bucket=self.analysis.bucket_name, key="THROW_ERROR")
        self.assertIsNone(ret)
    def test_get_data_set_logs(self):
        ret = get_data_set_logs(iam=self.iam, bucket=self.analysis.bucket_name, timestamp="1")
        self.assertIsNotNone(ret)
    def test_get_job_list_err(self):
        ret = get_job_list(iam=self.iam, bucket=self.analysis.bucket_name, folder="THROW_ERROR")
        self.assertEqual(ret, [])
    def test_get_files_detail_list_err(self):
        ret = get_files_detail_list(iam=self.iam, bucket=self.analysis.bucket_name, folder="THROW_ERROR")
        self.assertEqual(ret, [])
    def test_download_file_from_s3_err(self):
        key = "THROW/ERROR"
        file_key = "%s/%s" % (self.group.name, key)
        folder = generate_folder()
        ret = download_file_from_s3(iam=self.iam, bucket=self.analysis.bucket_name, key=file_key, folder=folder)
        self.assertIsNone(ret)