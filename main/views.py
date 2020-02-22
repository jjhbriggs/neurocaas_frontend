from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from base64 import b64encode
from .models import *
from account.models import *
from .demo_utils import *
# Create your views here.


class SelectBucketView(LoginRequiredMixin, View):
    """
        S3 Bucket Permission for CORS

            <?xml version="1.0" encoding="UTF-8"?>
            <CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <CORSRule>
                <AllowedOrigin>*</AllowedOrigin>
                <AllowedMethod>GET</AllowedMethod>
                <AllowedMethod>PUT</AllowedMethod>
                <AllowedMethod>POST</AllowedMethod>
                <AllowedMethod>DELETE</AllowedMethod>
                <MaxAgeSeconds>3000</MaxAgeSeconds>
                <ExposeHeader>ETag</ExposeHeader>
                <AllowedHeader>*</AllowedHeader>
            </CORSRule>
            </CORSConfiguration>

        Step 1 View
    """
    template_name = "main/step1.html"

    def get(self, request):
        buckets = Bucket.objects.all().order_by('name')
        return render(request=request, template_name=self.template_name, context={
            "buckets": buckets,
        })


class FileUploadView(LoginRequiredMixin, View):
    """
        Step 2 View for uploading files for analysis
    """
    template_name = "main/step2.html"

    def post(self, request):
        # create new subfolder with bucket
        bucket_name = request.POST['bucket']
        bucket = Bucket.objects.get(name=bucket_name)
        subfolder = SubFolder(bucket=bucket)

        # get aws credentials from iam
        iam = IAM.objects.filter(user=request.user).first()
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")

        return render(request=request, template_name=self.template_name, context={
            "subfolder": subfolder,
            "bucket": bucket_name,
            "id1": access_id,
            "id2": secret_key,
        })


class ProcessView(LoginRequiredMixin, View):
    """
        Step 3 View for processing files
    """
    template_name = "main/result.html"

    def get(self, request):
        return render(request=request, template_name=self.template_name)

    def post(self, request):

        iam = IAM.objects.filter(user=request.user).first()
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")
        buckets = Bucket.objects.all().order_by('name')

        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            "buckets": buckets,
        })


class ResultView(LoginRequiredMixin, View):
    """
        View for showing processing results
    """
    template_name = "main/result.html"

    def get(self, request):

        return render(request=request, template_name=self.template_name)


class CheckProcessView(View):
    """
    View for checking processing progress
    """

    def get(self, request):
        iam = IAM.objects.filter(user=request.user).first()
        process_name = request.GET['process']
        proc = Process.objects.get(name=process_name)
        res = check_process(iam=iam, process=proc)
        return JsonResponse({"status": True})
        # return JsonResponse({"status": res})


mp4_file = "cunninghamlabEPI/results/jobepi_demo/hp_optimum/epi_opt.mp4"
cert_file = "cunninghamlabEPI/results/jobepi_demo/logs/certificate.txt"
bucket_name = "epi-ncap"


class DemoView(LoginRequiredMixin, View):
    """
        View for demo in Feb
    """
    template_name = "main/demo.html"

    def get(self, request):
        bucket = Bucket.objects.get(name='epi-ncap')
        iam = IAM.objects.filter(user=request.user).first()
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")
        prefix = "cunninghamlabEPI/inputs"
        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            "bucket": bucket,
            "prefix": prefix
        })


def get_iam(request):
    return IAM.objects.filter(user=request.user).first()


class DemoResultView(LoginRequiredMixin, View):
    """
    Demo Result View
        """
    template_name = "main/demo_result.html"

    def get(self, request):
        iam = get_iam(request)

        cert_content = get_file_content(iam=iam, bucket=bucket_name, key=cert_file)
        return JsonResponse({
            "status": True,
            "cert_file": cert_content
        })

    def post(self, request):
        iam = IAM.objects.filter(user=request.user).first()

        timestamp = get_last_modified_timestamp(iam=iam, bucket=bucket_name, key=mp4_file)

        # remove last process files
        remove_files()

        return JsonResponse({
            "status": True,
            "timestamp": timestamp
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
