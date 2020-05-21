import json
import time
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

        if not analysis.check_iam(iam):
            messages.error(request, "You don't have permission for this analysis.")
            return redirect('/')

        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")
        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            'bucket': analysis.bucket_name,
            "data_dataset_dir": "%s/inputs" % iam.group.name,
            "data_config_dir": "%s/configs" % iam.group.name,
            "title": analysis.analysis_name,
            'iam': iam
        })

    def post(self, request, id):
        ana_id = request.session.get('ana_id', 1)
        analysis = Analysis.objects.get(pk=ana_id)

        iam = get_current_iam(request)
        data_set_files = request.POST.getlist('dataset_files[]')
        config_file = request.POST['config_file']
        cur_timestamp = int(time.time())

        process_data_set = []
        for file in data_set_files:
            from_key = "%s/inputs/%s" % (iam.group.name, file)
            process_data_set.append(from_key)

        from_key = "%s/configs/%s" % (iam.group.name, config_file)


        submit_data = {
            "dataname": process_data_set,
            "configname": from_key,
            "timestamp": str(cur_timestamp),
            # "instance_type": "t2.micro",
        }

        submit_key = "%s/submissions/submit.json" % iam.group.name
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

        # data_set files list
        folder = '%s/inputs' % iam.group
        data_set_keys = get_file_list(iam=iam, bucket=analysis.bucket_name, folder=folder)

        data_sets = []
        for key in data_set_keys:
            row = key.copy()
            path = key['key'].replace("%s/" % folder, "")
            row.update({'name': path})
            data_sets.append(row)

        # config files list
        folder = '%s/configs' % iam.group
        config_keys = get_file_list(iam=iam, bucket=analysis.bucket_name, folder=folder)
        configs = []
        for key in config_keys:
            row = key.copy()
            path = key['key'].replace("%s/" % folder, "")
            row.update({'name': path})
            content = get_file_content(iam=iam, bucket=analysis.bucket_name, key=key['key'])
            row.update({'content': content})
            configs.append(row)

        return JsonResponse({
            "status": 200,
            "data_sets": data_sets,
            "configs": configs
        })

    def delete(self, request, *args, **kwargs):
        ana_id = request.session.get('ana_id', 1)
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)

        put = QueryDict(request.body)

        file_name = put.get('file_name')
        _type = put.get('type')

        file_key = "%s/%s/%s" % (iam.group.name, _type, file_name)

        delete_file_from_bucket(iam=iam, bucket_name=analysis.bucket_name, key=file_key)

        return JsonResponse({
            "status": 200,
            "message": file_name
        })

    def put(self, request):
        ana_id = request.session.get('ana_id', 1)
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)
        put = QueryDict(request.body)

        file_name = put.get('file_name')
        _type = put.get('type')
        choice = put.get('choice', 'file')
        timestamp = put.get('timestamp', 0)

        file = ""
        if choice == 'file':
            file_key = "%s/%s/%s" % (iam.group.name, _type, file_name)
            file = get_download_file(iam=iam, bucket=analysis.bucket_name, key=file_key, timestamp=_type)
        else:
            """ Folder downloading here """
            root_folder = "%s/%s/" % (iam.group.name, _type)
            if _type == 'results':
                folder = "%s%s%s/%s" % (root_folder, analysis.result_prefix, timestamp, file_name)
            else:
                folder = "%s%s" % (root_folder, file_name)
            folder_path = download_directory_from_s3(iam=iam, bucket=analysis.bucket_name, folder=folder)

            zip_name = file_name.split('/')[-2] if file_name else _type
            zip_file = "static/downloads/%s/%s" % (time.time(), zip_name)
            if not os.path.exists(os.path.dirname(zip_file)):
                os.makedirs(os.path.dirname(zip_file))
            shutil.make_archive(zip_file, 'zip', folder_path)
            file = "%s.zip" % zip_file

        return JsonResponse({
            "status": 200,
            "message": file
        })


@method_decorator(csrf_exempt, name='dispatch')
class ResultView(LoginRequiredMixin, View):

    def get(self, request):
        ana_id = request.session.get('ana_id', 1)
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)
        timestamp = int(request.GET['timestamp']) if 'timestamp' in request.GET else 0

        cert_file = "%s/results/job__%s_%s/logs/certificate.txt" % (iam.group.name, analysis.bucket_name, timestamp)
        cert_timestamp = get_last_modified_timestamp(iam=iam, bucket=analysis.bucket_name, key=cert_file)

        if cert_timestamp == 0:
            cert_content = ""
        else:
            cert_content = get_file_content(iam=iam, bucket=analysis.bucket_name, key=cert_file)

        # store cert content to server
        parent_folder = "static/downloads"
        if not os.path.exists(parent_folder):
            os.mkdir(parent_folder)

        folder = "static/downloads/%s" % timestamp
        if not os.path.exists(folder):
            os.mkdir(folder)

        cert_path = "static/downloads/%s/certificate.txt" % timestamp
        file = open(cert_path, 'w')
        file.write(cert_content)
        file.close()

        return JsonResponse({
            "status": True,
            "cert_file": cert_content
        })

    def post(self, request):
        ana_id = request.session.get('ana_id', 1)
        analysis = Analysis.objects.get(pk=ana_id)
        iam = get_current_iam(request)

        timestamp = int(request.POST['timestamp'])
        result_folder = "%s/results/job__%s_%s/process_results" % (iam.group.name, analysis.bucket_name, timestamp)
        update_file = "%s/update.txt" % result_folder
        end_file = "%s/end.txt" % result_folder
        end_flag = False

        result_links = []
        update_timestamp = get_last_modified_timestamp(iam=iam, bucket=analysis.bucket_name, key=update_file)
        end_timestamp = get_last_modified_timestamp(iam=iam, bucket=analysis.bucket_name, key=end_file)
        if update_timestamp > 0 or end_timestamp > 0:
            previous_keys = json.loads(request.session.get('keys_%s' % timestamp, '[]'))
            result_links = json.loads(request.session.get('results_%s' % timestamp, '[]'))
            result_keys = get_list_keys(iam=iam, bucket=analysis.bucket_name, folder=result_folder)
            print(result_keys)

            for key in result_keys:
                if key in previous_keys:
                    continue
                link = get_download_file(iam=iam, bucket=analysis.bucket_name, key=key, timestamp=timestamp)
                path = key.replace('%s/results/job__%s_%s/' % (iam.group.name, analysis.bucket_name, timestamp), '')
                result_links.append({'link': link, 'path': path})
                previous_keys.append(key)
            request.session['keys_%s' % timestamp] = json.dumps(previous_keys)
            request.session['results_%s' % timestamp] = json.dumps(result_links)

            if end_timestamp > 0:
                del request.session['keys_%s' % timestamp]
                del request.session['results_%s' % timestamp]
                end_flag = True

        data_set_logs = []
        log_dir = "%s/results/job__%s_%s/logs/" % (iam.group.name, analysis.bucket_name, timestamp)
        data_set_logs_keys = get_dataset_logs(iam=iam, bucket=analysis.bucket_name, log_dir=log_dir)
        for key in data_set_logs_keys:
            path = key.replace("%s/results/job__%s_%s/" % (iam.group.name, analysis.bucket_name, timestamp), "")
            data_set_logs.append({'link': get_download_file(iam, analysis.bucket_name, key, timestamp), 'path': path})

        return JsonResponse({
            "status": 200,
            "result_links": result_links,
            "data_set_logs": data_set_logs,
            "end": end_flag
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


class AnalysisIntroView(View):
    template_name = "main/analysis_intro.html"

    def get(self, request, id):
        analysis = Analysis.objects.get(pk=id)
        iam = get_current_iam(request)

        return render(request=request, template_name=self.template_name, context={
            "analysis": analysis,
            'iam': iam
        })
