from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
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
        aws_req = AWSRequest.objects.filter(user=request.user).first()
        if aws_req:
            aws_req.status = STATUS_PENDING
        else:
            aws_req = AWSRequest(user=request.user)
        aws_req.save()
        return redirect('profile')


class ChangePWDView(View):
    template_name = "account/change_password.html"

    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, template_name=self.template_name, context={
            "user": request.user, "form": form
        })

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'An Error was occurred, Please try again!')
            return redirect('change_pwd')
