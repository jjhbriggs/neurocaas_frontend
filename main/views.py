from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
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
        return render(request=request, template_name=self.template_name, context={})


class ProcessView(LoginRequiredMixin, View):
    pass
