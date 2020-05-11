import json
import time
from base64 import b64encode

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from account.forms import UserLoginForm, UserCreationForm
from account.models import *
from .utils import *

# Create your views here.


class HomeView(View):
    """
        Home Page View
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
            # context = {
            #     "logged_in": True
            # }
            return redirect(next_url)
        return render(request=request, template_name=self.template_name, context=context)


@method_decorator(csrf_exempt, name='dispatch')
class ProcessView(LoginRequiredMixin, View):
    """
        Main View
    """
    template_name = "main/process.html"

    def get(self, request, id):
        request.session['ana_id'] = id
        analysis = Analysis.objects.get(pk=id)
        iam = get_current_iam(request)

        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")
        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            'bucket': analysis.bucket_name,
            "data_dataset_dir": "%s/inputs" % iam.group,
            "data_config_dir": "%s/configs" % iam.group,
            "title": analysis.analysis_name,
            'iam': iam
        })

    def post(self, request, id):
        ana_id = request.session.get('ana_id', 1)
        analysis = Analysis.objects.get(pk=ana_id)

        iam = get_current_iam(request)
        dataset_files = request.POST.getlist('dataset_files[]')
        config_file = request.POST['config_file']

        # remove existing dataset files from epi bucket
        cur_timestamp = int(time.time())
        dataset_dir = "%s/%s/%s" % (iam.group, analysis.dataset_path, cur_timestamp)

        # copy dataset files to work_bucket
        for file in dataset_files:
            from_key = "%s/%s/dataset/%s/%s" % (analysis.upload_folder, iam.aws_user, iam.group, file)
            to_key = "%s/%s" % (dataset_dir, file)
            copy_file_to_bucket(iam=iam, from_bucket=analysis.bucket_name, from_key=from_key,
                                to_bucket=analysis.bucket_name, to_key=to_key)

        # copy config file to work_bucket
        config_to_key = "%s/%s/config_%s.json" % (iam.group, analysis.config_path, cur_timestamp)
        from_key = "%s/%s/config/%s/%s" % (analysis.upload_folder, iam.aws_user, iam.group, config_file)
        copy_file_to_bucket(iam=iam, from_bucket=analysis.bucket_name, from_key=from_key, to_bucket=analysis.bucket_name,
                            to_key=config_to_key)

        submit_data = {
            "dataname": dataset_dir + "/",
            "configname": config_to_key,
            "timestamp": str(cur_timestamp),
            # "instance_type": "t2.micro",
        }

        submit_key = "%s/%s" % (iam.group, analysis.submit_path)
        create_submit_json(iam=iam, work_bucket=analysis.bucket_name, key=submit_key, json_data=submit_data)

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
        analysis = Analysis.objects.get(pk=ana_id)

        iam = get_current_iam(request)

        # dataset files list
        folder = '%s/inputs' % iam.group
        dataset_keys = get_file_list(iam=iam, bucket=analysis.bucket_name, folder=folder)

        datasets = []
        for key in dataset_keys:
            row = key.copy()
            row.update({'name': get_name_only(key=key['key'])})
            datasets.append(row)
        # [datasets.append(key.update({'name': get_name_only(key=key['key'])})) for key in dataset_keys]

        # config files list
        folder = '%s/configs' % iam.group
        config_keys = get_file_list(iam=iam, bucket=analysis.bucket_name, folder=folder)
        configs = []
        for key in config_keys:
            row = key.copy()
            row.update({'name': get_name_only(key=key['key'])})
            content = get_file_content(iam=iam, bucket=analysis.bucket_name, key=key['key'])
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
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)
        timestamp = int(request.GET['timestamp']) if 'timestamp' in request.GET else 0

        cert_file = "%s/%s/job__%s_%s/logs/certificate.txt" % (iam.group, analysis.result_path, analysis.bucket_name, timestamp)
        cert_timestamp = get_last_modified_timestamp(iam=iam, bucket=analysis.bucket_name, key=cert_file)

        if cert_timestamp == 0:
            cert_content = ""
        else:
            cert_content = get_file_content(iam=iam, bucket=analysis.bucket_name, key=cert_file)

        dtset_logs = []
        log_dir = "%s/%s/job__%s_%s/logs/" % (iam.group, analysis.result_path, analysis.bucket_name, timestamp)
        dtset_logs_keys = get_dataset_logs(iam=iam, bucket=analysis.bucket_name, log_dir=log_dir)
        for key in dtset_logs_keys:
            path = key.replace("%s/%s/job__%s_%s/" % (iam.group, analysis.result_path, analysis.bucket_name, timestamp), "")
            dtset_logs.append({'link': get_download_file(iam, analysis.bucket_name, key, timestamp), 'path': path})

        return JsonResponse({
            "status": True,
            "cert_file": cert_content,
            "dtset_logs": dtset_logs
        })

    def post(self, request):
        # config = Analysis.objects.filter(analysis_name=analysis_name).first()
        ana_id = request.session.get('ana_id', 1)
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)
        timestamp = int(request.POST['timestamp'])
        result_items = json.loads(config.result_items)
        result_keys = []
        for item in result_items:
            file_key = "%s/%s/job__%s_%s/%s" % (iam.group, analysis.result_path, analysis.bucket_name, timestamp, item['path'])
            result_keys.append({'key': file_key, 'path': item['path']})

        file_timestamp = get_last_modified_timestamp(iam=iam, bucket=analysis.bucket_name, key=result_keys[0]['key'])

        result_links = []
        if file_timestamp > 0:
            for key in result_keys:
                link = get_download_file(iam=iam, bucket=analysis.bucket_name, key=key['key'], timestamp=timestamp)
                result_links.append({'link': link, 'path': key['path']})

            # remove used dataset and config files
            dataset_dir = "%s/%s/%s" % (iam.group, analysis.dataset_path, timestamp)
            delete_jsons_from_bucket(iam=iam, bucket_name=analysis.bucket_name, prefix="%s/" % dataset_dir)
            # remove config file from epi bucket
            config_to_key = "%s/%s/config_%s.json" % (iam.group, analysis.config_path, timestamp)
            delete_file_from_bucket(iam=iam, bucket_name=analysis.bucket_name, key=config_to_key)

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
            'analyses': analyses,
            'iam': get_current_iam(request)
        })


class AnalysisIntroView(LoginRequiredMixin, View):
    template_name = "main/analysis_intro.html"

    def get(self, request, id):
        analysis = Analysis.objects.get(pk=id)
        iam = get_current_iam(request)


        return render(request=request, template_name=self.template_name, context={
            "analysis": analysis,
            'iam': iam
        })
