from django.shortcuts import render
from django.views.generic import TemplateView, View

# Create your views here.


class HomeView(TemplateView):
    template_name = "main/home.html"


class FileUploadView(View):
    template_name = "main/file_upload.html"

    def get(self, request):
        return render(request=request, template_name=self.template_name, context={})
