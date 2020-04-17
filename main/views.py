from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from base64 import b64encode
from .models import *
from account.models import *
from .demo_utils import *
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from account.forms import UserLoginForm, UserCreationForm
import time, json

# Create your views here.


"""
    Views for Demo page 
"""

result_dir = "cunninghamlabEPI/results"
work_bucket = "epi-ncap"
upload_dir = "cunninghamlabEPI/inputs"
submit_file_name = "episubmit.json"
analysis_name = 'Epi-ncap-stable'


# config_name = 'Epi-ncap'


class HomeView(View):
    """
        Home Page View
        """
    template_name = "main/home.html"

    def get(self, request):

        if request.user.is_anonymous:
            next_url = request.GET.get('next') if 'next' in request.GET else '/home/'
            context = {
                "logged_in": False,
                "login_form": UserLoginForm(),
                "reg_form": UserCreationForm(),
                "next": next_url
            }
        else:
            context = {
                "logged_in": True
            }
        return render(request=request, template_name=self.template_name, context=context)


def get_iam(request):
    return IAM.objects.filter(user=request.user).first()


@method_decorator(csrf_exempt, name='dispatch')
class ProcessView(LoginRequiredMixin, View):
    """
        Main View
    """
    template_name = "main/process.html"

    def get(self, request):
        ana_id = request.GET.get('id') if 'id' in request.GET else 1
        request.session['ana_id'] = ana_id
        config = Analysis.objects.get(pk=ana_id)

        iam = IAM.objects.filter(user=request.user).first()
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")
        root_folder = "%s/%s" % (config.upload_folder, iam.aws_user)
        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            'bucket': config.bucket_name,
            "data_dataset_dir": "%s/dataset" % root_folder,
            "data_config_dir": "%s/config" % root_folder,
        })

    def post(self, request):
        # config = Analysis.objects.filter(analysis_name=analysis_name).first()
        ana_id = request.session.get('ana_id', 1)
        config = Analysis.objects.get(pk=ana_id)

        iam = IAM.objects.filter(user=request.user).first()
        dataset_files = request.POST.getlist('dataset_files[]')
        config_file = request.POST['config_file']

        # remove existing dataset files from epi bucket
        cur_timestamp = int(time.time())
        dataset_dir = "%s/%s" % (config.dataset_path, cur_timestamp)

        # copy dataset files to work_bucket
        for file in dataset_files:
            from_key = "%s/%s/dataset/%s" % (config.upload_folder, iam.aws_user, file)
            to_key = "%s/%s" % (dataset_dir, file)
            copy_file_to_bucket(iam=iam, from_bucket=config.bucket_name, from_key=from_key,
                                to_bucket=config.bucket_name, to_key=to_key)

        # copy config file to work_bucket
        config_to_key = "%s/config_%s.json" % (config.config_path, cur_timestamp)
        from_key = "%s/%s/config/%s" % (config.upload_folder, iam.aws_user, config_file)
        copy_file_to_bucket(iam=iam, from_bucket=config.bucket_name, from_key=from_key, to_bucket=config.bucket_name,
                            to_key=config_to_key)

        submit_data = {
            "dataname": dataset_dir + "/",
            "configname": config_to_key,
            "timestamp": str(cur_timestamp),
            # "instance_type": "t2.micro",
        }

        create_submit_json(iam=iam, work_bucket=config.bucket_name, key=config.submit_path, json_data=submit_data)

        # store timestamp in session
        request.session['last_timestamp'] = cur_timestamp

        return JsonResponse({"status": True, "timestamp": cur_timestamp})


@method_decorator(csrf_exempt, name='dispatch')
class UserFilesView(LoginRequiredMixin, View):
    """
        View to manage files for each user
        """

    def get(self, request):
        """
            return dataset and config files user uploaded before
        """
        # config = Analysis.objects.filter(analysis_name=analysis_name).first()
        ana_id = request.session.get('ana_id', 1)
        config = Analysis.objects.get(pk=ana_id)

        iam = IAM.objects.filter(user=request.user).first()

        # dataset files list
        root_folder = "%s/%s" % (config.upload_folder, iam.aws_user)
        folder = '%s/dataset' % root_folder
        dataset_keys = get_file_list(iam=iam, bucket=config.bucket_name, folder=folder)

        datasets = []
        for key in dataset_keys:
            row = key.copy()
            row.update({'name': get_name_only(key=key['key'])})
            datasets.append(row)
        # [datasets.append(key.update({'name': get_name_only(key=key['key'])})) for key in dataset_keys]

        # config files list
        folder = '%s/config' % root_folder
        config_keys = get_file_list(iam=iam, bucket=config.bucket_name, folder=folder)
        configs = []
        for key in config_keys:
            row = key.copy()
            row.update({'name': get_name_only(key=key['key'])})
            content = get_file_content(iam=iam, bucket=config.bucket_name, key=key['key'])
            row.update({'content': content})
            configs.append(row)

        # [config_names.append(get_name_only(key=key)) for key in config_keys]

        return JsonResponse({
            "status": 200,
            "datasets": datasets,
            "configs": configs
        })

    def delete(self, request):
        file_name = request.GET['file_name']
        return JsonResponse({
            "status": 200,
            "message": file_name
        })


@method_decorator(csrf_exempt, name='dispatch')
class ResultView(LoginRequiredMixin, View):

    def get(self, request):
        # config = Analysis.objects.filter(analysis_name=analysis_name).first()
        ana_id = request.session.get('ana_id', 1)
        config = Analysis.objects.get(pk=ana_id)
        iam = get_iam(request)
        timestamp = int(request.GET['timestamp']) if 'timestamp' in request.GET else 0

        cert_file = "%s/job__%s_%s/logs/certificate.txt" % (config.result_path, config.bucket_name, timestamp)
        cert_timestamp = get_last_modified_timestamp(iam=iam, bucket=config.bucket_name, key=cert_file)

        if cert_timestamp == 0:
            cert_content = ""
        else:
            cert_content = get_file_content(iam=iam, bucket=config.bucket_name, key=cert_file)

        dtset_logs = []
        log_dir = "%s/job__%s_%s/logs/" % (config.result_path, config.bucket_name, timestamp)
        dtset_logs_keys = get_dataset_logs(iam=iam, bucket=config.bucket_name, log_dir=log_dir)
        for key in dtset_logs_keys:
            path = key.replace("%s/job__%s_%s/" % (config.result_path, config.bucket_name, timestamp), "")
            dtset_logs.append({'link': get_download_file(iam, config.bucket_name, key, timestamp), 'path': path})

        return JsonResponse({
            "status": True,
            "cert_file": cert_content,
            "dtset_logs": dtset_logs
        })

    def post(self, request):
        # config = Analysis.objects.filter(analysis_name=analysis_name).first()
        ana_id = request.session.get('ana_id', 1)
        config = Analysis.objects.get(pk=ana_id)
        iam = IAM.objects.filter(user=request.user).first()
        timestamp = int(request.POST['timestamp'])
        result_items = json.loads(config.result_items)
        result_keys = []
        for item in result_items:
            file_key = "%s/job__%s_%s/%s" % (config.result_path, config.bucket_name, timestamp, item['path'])
            result_keys.append({'key': file_key, 'path': item['path']})

        file_timestamp = get_last_modified_timestamp(iam=iam, bucket=config.bucket_name, key=result_keys[0]['key'])

        result_links = []
        if file_timestamp > 0:
            for key in result_keys:
                link = get_download_file(iam=iam, bucket=config.bucket_name, key=key['key'], timestamp=timestamp)
                result_links.append({'link': link, 'path': key['path']})

            # remove used dataset and config files
            dataset_dir = "%s/%s" % (config.dataset_path, timestamp)
            delete_jsons_from_bucket(iam=iam, bucket_name=config.bucket_name, prefix="%s/" % dataset_dir)
            # remove config file from epi bucket
            config_to_key = "%s/config_%s.json" % (config.config_path, timestamp)
            delete_file_from_bucket(iam=iam, bucket_name=config.bucket_name, key=config_to_key)

        return JsonResponse({
            "status": 200,
            'result_links': result_links
        })


""" Intro & Analysis Intro pages """


class IntroView(View):
    template_name = "main/intro.html"

    def get(self, request):
        analyses = Analysis.objects.all()
        return render(request=request, template_name=self.template_name, context={
            'analyses': analyses
        })


class AnalysisIntroView(LoginRequiredMixin, View):
    template_name = "main/analysis_intro.html"

    def get(self, request):
        ind = request.GET.get('id') if 'id' in request.GET else 1
        analysis = Analysis.objects.get(pk=ind)
        return render(request=request, template_name=self.template_name, context={
            "analysis": analysis
        })
