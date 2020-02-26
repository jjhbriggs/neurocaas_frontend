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

# Create your views here.


"""
    Views for Demo page 
"""

mp4_file = "cunninghamlabEPI/results/jobepi_demo/hp_optimum/epi_opt.mp4"
cert_file = "cunninghamlabEPI/results/jobepi_demo/logs/certificate.txt"
log_dir = "cunninghamlabEPI/results/jobepi_demo/logs"
dataset_dir = "cunninghamlabEPI/inputs/epidata"
bucket_name = "epi-ncap"
upload_dir = "cunninghamlabEPI/inputs"


class HomeView(View):
    """
        Home Page View
        """
    template_name = "main/home.html"

    def get(self, request):

        if request.user.is_anonymous:
            context = {
                "logged_in": False,
                "login_form": UserLoginForm(),
                "reg_form": UserCreationForm()
            }
        else:
            context = {
                "logged_in": True
            }
        return render(request=request, template_name=self.template_name, context=context)


def get_iam(request):
    return IAM.objects.filter(user=request.user).first()


class DemoView(LoginRequiredMixin, View):
    """
        View for demo in Feb
    """
    template_name = "main/demo.html"

    def get(self, request):
        iam = IAM.objects.filter(user=request.user).first()
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")

        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            "bucket": bucket_name,
            "upload_dir": upload_dir,
            'dataset_dir': dataset_dir
        })


@method_decorator(csrf_exempt, name='dispatch')
class DemoResultView(LoginRequiredMixin, View):
    """
    Demo Result View
        """
    template_name = "main/demo_result.html"

    def get(self, request):
        iam = get_iam(request)
        from_timestamp = int(request.GET['timestamp']) if 'timestamp' in request.GET else 0
        timestamp = get_last_modified_timestamp(iam=iam, bucket=bucket_name, key=cert_file)
        if from_timestamp > timestamp:
            cert_content = ""
        else:
            cert_content = get_file_content(iam=iam, bucket=bucket_name, key=cert_file)
        return JsonResponse({
            "status": True,
            "cert_file": cert_content
        })

    def post(self, request):
        iam = IAM.objects.filter(user=request.user).first()
        from_timestamp = int(request.POST['timestamp'])

        timestamp = get_last_modified_timestamp(iam=iam, bucket=bucket_name, key=mp4_file)

        # video & dataset files logs
        video_link = None
        dtset_logs = []
        if from_timestamp > timestamp:
            # remove last process files
            remove_files()
        else:
            video_link = get_download_file(iam, bucket_name, mp4_file)
            dtset_logs_keys = get_dataset_logs(iam=iam, bucket=bucket_name)
            dtset_logs = []
            for key in dtset_logs_keys:
                dtset_logs.append(get_download_file(iam, bucket_name, key))

        return JsonResponse({
            "status": 200,
            "video_link": video_link,
            "dtset_logs": dtset_logs
        })

        """
        file_name = request.POST['file']
        file = FileItem(name=file_name, bucket=bucket, uploaded=True)
        file.save()

        proc = Process(iam=iam, uploaded_file=file)
        proc.save()
        url = '/demo_result?process=%s' % proc.name
        return redirect(url)
        """


"""
class DemoCheckView(LoginRequiredMixin, View):

    def get(self, request):

        action = request.POST['action']
        timestamp = request.POST['timestamp']

        iam = IAM.objects.filter(user=request.user).first()
        proc = Process.objects.get(name=request.GET['process'])
        link = check_process(process=proc, iam=iam)

        return JsonResponse({
            "status": True,
            "link": link
        })
"""
