from base64 import b64encode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, QueryDict
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from account.forms import UserLoginForm, UserCreationForm
from .models import *
from .utils import *
from django.contrib import messages

import shutil


# Create your views here.
class IntroView(View):
    """
        Intro View (Index View).
        Detail of NeuroCAAS and Available Analyses.
    """
    template_name = "main/intro.html"

    def get(self, request):
        main_analyses = Analysis.objects.filter(custom=False).all()
        return render(request=request,
                      template_name=self.template_name,
                      context={
                          'main_analyses': main_analyses,
                          'iam': get_current_iam(request),
                          'user': get_current_user(request),
                          'logged_in': not request.user.is_anonymous
                      })


class AnalysisListView(View):
    """
        Analysis List View.
        List of all Available and Custom Analyses.
    """
    template_name = "main/analysis_list.html"

    def get(self, request):
        main_analyses = Analysis.objects.filter(custom=False).all()
        custom_analyses = Analysis.objects.filter(custom=True).all()

        return render(request=request,
                      template_name=self.template_name,
                      context={
                          'main_analyses': main_analyses,
                          'custom_analyses': custom_analyses,
                          'iam': get_current_iam(request),
                          'user': get_current_user(request),
                          'logged_in': not request.user.is_anonymous
                      })

class PermissionView(View):
    """
        Permission Page View.
    """

    template_name = "main/permissions.html"

    def get(self, request):
        return render(request=request,
                      template_name=self.template_name,
                      context={
                          'iam': get_current_iam(request),
                          'user': get_current_user(request)
                      })


class QAView(View):
    """
        Q/A Page View.
    """

    template_name = "main/qa_page.html"

    def get(self, request):
        return render(request=request,
                      template_name=self.template_name,
                      context={
                          'iam': get_current_iam(request),
                          'user': get_current_user(request),
                          'logged_in': not request.user.is_anonymous
                      })


class AnalysisIntroView(View):
    """
        Intro View of Analysis.
        Detail of Analysis : Description and Useful link.
    """
    template_name = "main/analysis_intro.html"

    def get(self, request, ana_id):
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)
        access = False
        if not request.user.is_anonymous and iam:
            access = analysis.check_iam(iam)
        return render(
            request=request,
            template_name=self.template_name,
            context={
                "analysis": analysis,
                'iam': iam,
                'user': get_current_user(request),
                'access': access,
                'logged_in': not request.user.is_anonymous
            })


class HomeView(View):
    """
        View to check if logged in or not, if not, redirected to login page.
    """
    template_name = "main/home.html"

    def get(self, request):
        next_url = request.GET.get('next') if 'next' in request.GET else '/'
        if request.user.is_anonymous:
            next_url = request.GET.get('next') if 'next' in request.GET else '/home/'
            context = {
                "logged_in": False,
                "login_form": UserLoginForm(),
                "reg_form": UserCreationForm(),
                "next": next_url
            }
        else:
            return redirect(next_url)

        return render(
            request=request,
            template_name=self.template_name,
            context=context
        )


class JobListView(LoginRequiredMixin, View):
    """
        Shows List of Jobs done for analysis.
    """
    template_name = 'main/job_history.html'

    def get(self, request, ana_id):
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)
        results_folder = '%s/results' % iam.group

        if not analysis.check_iam(iam):
            messages.error(request, "Your AWS group doesn't have permission to use this analysis.")
            return redirect('/')
        job_list = get_job_list(iam=iam, bucket=analysis.bucket_name, folder=results_folder)
        return render(
            request=request,
            template_name=self.template_name,
            context={
                "analysis": analysis,
                'iam': iam,
                'user': get_current_user(request),
                'job_list': job_list,
                'logged_in': not request.user.is_anonymous
            })


class JobDetailView(LoginRequiredMixin, View):
    """
        Shows detail of Job done for analysis, User can check and download the content of job files.
    """
    template_name = 'main/job_detail.html'

    def get(self, request, ana_id, job_id):
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)

        if not analysis.check_iam(iam):
            messages.error(request, "Your AWS group doesn't have permission to use this analysis.")
            return redirect('/')

        result_folder = "%s/results/%s" % (iam.group.name, job_id)
        result_keys = get_list_keys(iam=iam,
                                    bucket=analysis.bucket_name,
                                    folder=result_folder,
                                    un_cert=False)
        job_detail = [item.replace(result_folder, '/results') for item in result_keys]
        print(job_detail)
        return render(
            request=request,
            template_name=self.template_name,
            context={
                "analysis": analysis,
                'iam': iam,
                'user': get_current_user(request),
                'logged_in': not request.user.is_anonymous,
                'job_id': job_id,
                'job_detail': json.dumps(job_detail),
                'timestamp': job_id.split('_')[-1]
            })


@method_decorator(csrf_exempt, name='dispatch')
class FilesView(LoginRequiredMixin, View):
    """
        View to manage files for each analysis, get and download, delete file and folders.
    """

    def get(self, request, ana_id):
        """
            Download file from s3 and return downloaded file path.
         """
        analysis = get_current_analysis(ana_id)
        iam = get_current_iam(request)

        key = request.GET.get('key', None)
        file_key = "%s/%s" % (iam.group.name, key)
        folder = generate_folder()

        downloaded_path = download_file_from_s3(iam=iam, bucket=analysis.bucket_name, key=file_key, folder=folder)

        return JsonResponse({
            "status": 200,
            "message": downloaded_path
        })

    def post(self, request, ana_id):
        """
            Download folder from s3, zipping folder and return zip file path.
        """

        analysis = get_current_analysis(ana_id)
        iam = get_current_iam(request)

        key = request.POST.get('key', None)
        folder_key = "%s/%s" % (iam.group.name, key)

        downloaded_path = download_directory_from_s3(
            iam=iam,
            bucket=analysis.bucket_name,
            folder=folder_key, un_cert=False)

        zip_name = key.split('/')[-1]
        zip_path = "static/downloads/%s/%s" % (time.time(), zip_name)
        mkdir(os.path.dirname(zip_path))

        shutil.make_archive(zip_path, 'zip', downloaded_path)
        file = "%s.zip" % zip_path

        return JsonResponse({
            "status": 200,
            "message": file
        })

    def delete(self, request, ana_id):
        """
            Delete a file from inputs or config folder on s3 by filename.
        """
        analysis = get_current_analysis(ana_id)
        iam = get_current_iam(request)

        dicts = QueryDict(request.body)
        key = dicts.get('key')

        file_key = "%s/%s" % (iam.group.name, key)
        print(file_key)

        if file_key.endswith("/"):
            msg = delete_folder_from_bucket(iam=iam, bucket=analysis.bucket_name, prefix=file_key)
        else:
            msg = delete_file_from_bucket(iam=iam, bucket=analysis.bucket_name, key=file_key)

        return JsonResponse({
            "status": 200,
            "message": msg
        })


@method_decorator(csrf_exempt, name='dispatch')
class UserFilesView(LoginRequiredMixin, View):
    """
        Return list of inputs and configs files for analysis.
    """

    def get(self, request, ana_id):
        """
            Return inputs and config files users uploaded so far.
        """
        analysis = get_current_analysis(ana_id)
        iam = get_current_iam(request)

        # data_set files list
        data_set_folder = '%s/inputs' % iam.group
        data_set_keys = get_files_detail_list(iam=iam, bucket=analysis.bucket_name, folder=data_set_folder)

        data_sets = []
        for key in data_set_keys:
            row = key.copy()
            path = key['key'].replace("%s/" % data_set_folder, "")
            row.update({'name': path})
            data_sets.append(row)

        # config files list
        config_folder = '%s/configs' % iam.group
        config_keys = get_files_detail_list(iam=iam, bucket=analysis.bucket_name, folder=config_folder)
        configs = []
        for key in config_keys:
            row = key.copy()
            path = key['key'].replace("%s/" % config_folder, "")
            content = get_file_content(iam=iam, bucket=analysis.bucket_name, key=key['key'])
            row.update({'content': content, 'name': path})
            configs.append(row)

        return JsonResponse({
            "status": 200,
            "data_sets": data_sets,
            "configs": configs
        })


@method_decorator(csrf_exempt, name='dispatch')
class ProcessView(LoginRequiredMixin, View):
    """
        Processing View.
    """
    template_name = "main/process.html"

    def get(self, request, ana_id):
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)

        if not analysis.check_iam(iam):
            messages.error(request, "Your AWS group doesn't have permission to use this analysis.")
            return redirect('/')

        # convert aws keys to base64 string
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")

        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            'bucket': analysis.bucket_name,
            "data_set_dir": "%s/inputs" % iam.group.name,
            "config_dir": "%s/configs" % iam.group.name,
            "title": analysis.analysis_name,
            'iam': iam,
            'user': get_current_user(request),
            'logged_in': not request.user.is_anonymous,
            'analysis': analysis
        })

    def post(self, request, ana_id):
        """
            Start new processing with analysis ID, inputs and config files.
        """
        analysis = get_current_analysis(ana_id)
        iam = get_current_iam(request)

        data_set_files = request.POST.getlist('data_set_files[]')
        config_file = request.POST['config_file']
        cur_timestamp = int(time.time())

        process_data_set = []
        for file in data_set_files:
            process_data_set.append("%s/inputs/%s" % (iam.group.name, file))

        submit_data = {
            "dataname": process_data_set,
            "configname": "%s/configs/%s" % (iam.group.name, config_file),
            "timestamp": str(cur_timestamp),
            # "instance_type": "t2.micro",
        }

        submit_key = "%s/submissions/submit.json" % iam.group.name
        create_submit_json(iam=iam,
                           bucket=analysis.bucket_name,
                           key=submit_key,
                           json_data=submit_data)

        return JsonResponse({
            "status": True,
            "timestamp": cur_timestamp
        })


@method_decorator(csrf_exempt, name='dispatch')
class ResultView(LoginRequiredMixin, View):
    """
        Process results View.
    """
    def get(self, request, ana_id):
        """
            Retrieve Certificate.txt content from s3 and return it.
        """
        analysis = get_current_analysis(ana_id)
        iam = get_current_iam(request)
        timestamp = int(request.GET['timestamp']) if 'timestamp' in request.GET else 0

        cert_file = "%s/results/job__%s_%s/logs/certificate.txt" % (iam.group.name, analysis.bucket_name, timestamp)
        cert_timestamp = get_last_modified_timestamp(
            iam=iam,
            bucket=analysis.bucket_name,
            key=cert_file)

        if cert_timestamp == 0:
            cert_content = ""
        else:
            cert_content = get_file_content(iam=iam,
                                            bucket=analysis.bucket_name,
                                            key=cert_file)

        return JsonResponse({
            "status": True,
            "cert_file": cert_content
        })

    def post(self, request, ana_id):
        """
            Retrieve files from results and logs folder on s3 and return them.
            Checking update.txt and end.txt so that determine analysis was finished or not.
        """
        analysis = get_current_analysis(ana_id)
        iam = get_current_iam(request)
        timestamp = int(request.POST['timestamp'])

        result_folder = "%s/results/job__%s_%s" % (iam.group.name, analysis.bucket_name, timestamp)
        end_file = "%s/process_results/end.txt" % result_folder
        end_flag = False

        result_links = []

        end_timestamp = get_last_modified_timestamp(iam=iam,
                                                    bucket=analysis.bucket_name,
                                                    key=end_file)
        result_keys = get_list_keys(iam=iam,
                                    bucket=analysis.bucket_name,
                                    folder=result_folder,
                                    un_cert=False)
        for key in result_keys:
            path = key.replace('%s/results/job__%s_%s/' % (iam.group.name, analysis.bucket_name, timestamp), '')
            result_links.append({'path': path})

        if end_timestamp > 0:
            end_flag = True

        return JsonResponse({
            "status": 200,
            "result_links": result_links,
            "end": end_flag
        })


class TestView(LoginRequiredMixin, View):

    def get(self, request):
        analysis = Analysis.objects.get(pk=2)
        iam = get_current_iam(request)

        if not analysis.check_iam(iam):
            messages.error(request, "Your AWS group doesn't have permission to use this analysis.")
            return redirect('/')

        # convert aws keys to base64 string
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")

        return render(request=request, template_name="main/test.html", context={
            "id1": access_id,
            "id2": secret_key,
            'bucket': analysis.bucket_name,
            "data_set_dir": "%s/inputs" % iam.group.name,
            "config_dir": "%s/configs" % iam.group.name,
            "title": analysis.analysis_name,
            'iam': iam,
            'user': get_current_user(request),
            'logged_in': not request.user.is_anonymous,
            'analysis': analysis
        })
