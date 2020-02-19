from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from base64 import b64encode
from .models import *
from account.models import *
import boto3
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


def check_progress(process_id, iam):
    return True


class CheckProcessView(View):
    """
    View for checking processing progress
    """

    def get(self, request):
        iam = IAM.objects.filter(user=request.user).first()
        process_id = request.GET['process_id']
        res = check_progress(process_id=process_id, iam=iam)
        return JsonResponse({"status": res})
