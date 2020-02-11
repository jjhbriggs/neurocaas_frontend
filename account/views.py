from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import View

# Create your views here.


class ProfileView(View):
    template_name = "account/profile.html"

    def get(self, request):
        return render(request, template_name=self.template_name, context={"user": request.user})


class AWSCredRequestView(View):

    def get(self, request):
        pass