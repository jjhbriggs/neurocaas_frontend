from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from base64 import b64encode
from .models import *
from account.models import *
# Create your views here.


class FileUploadView(LoginRequiredMixin, View):
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

    """
    template_name = "main/file_upload.html"

    def get(self, request):
        iam = IAM.objects.filter(user=request.user).first()
        secret_key = b64encode(b64encode(iam.aws_secret_access_key.encode('utf-8'))).decode("utf-8")
        access_id = b64encode(b64encode(iam.aws_access_key.encode('utf-8'))).decode("utf-8")
        buckets = Bucket.objects.all().order_by('name')

        return render(request=request, template_name=self.template_name, context={
            "id1": access_id,
            "id2": secret_key,
            "buckets": buckets,
        })


class ProcessView(LoginRequiredMixin, View):
    pass
