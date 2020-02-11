from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.views.generic import View
from .models import *
# Create your views here.


class ProfileView(View):
    template_name = "account/profile.html"

    def get(self, request):
        aws_req = AWSRequest.objects.filter(user=request.user).first()
        return render(request, template_name=self.template_name, context={
            "user": request.user,
            "aws_req": aws_req
        })


class AWSCredRequestView(View):

    def get(self, request):
        pass