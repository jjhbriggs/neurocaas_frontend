from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View
from .models import *
from .forms import *
from ncap.backends import authenticate


# Create your views here.


class LoginView(View):
    template_name = "account/login.html"

    def get(self, request):
        if request.user:
            return redirect('profile')

        form = UserLoginForm()
        return render(request, template_name=self.template_name, context={'form': form})

    def post(self, request):
        form = UserLoginForm(request.POST)
        user = authenticate(aws_access_key=form.data['aws_access_key'],
                            aws_secret_access_key=form.data['aws_secret_access_key'])
        if user:
            login(request, user)
            return redirect('profile')

        messages.error(request=request, message="Invalid Credentials, Try again!")
        return redirect('login')


class SignUpView(View):
    template_name = "account/signup.html"

    def get(self, request):
        form = UserCreationForm()
        return render(request=request, template_name=self.template_name, context={
            "form": form
        })

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # create AWS Request object for created user
            aws_req = AWSRequest(user=user)
            aws_req.save()

            messages.success(request, 'Successfully Registered, Please wait for email from us!')
            return redirect('profile')
        return render(request, template_name=self.template_name, context={"form": form})


class ProfileView(LoginRequiredMixin, View):
    template_name = "account/profile.html"

    def get(self, request):
        aws_req = AWSRequest.objects.filter(user=request.user).first()
        iam = IAM.objects.filter(user=request.user).first()
        return render(request, template_name=self.template_name, context={
            "user": request.user,
            "aws_req": aws_req,
            "iam": iam
        })

    def post(self, request):
        form = ProfileChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()

            messages.success(request, 'Successfully updated!')

        return redirect('profile')


class AWSCredRequestView(LoginRequiredMixin, View):

    def get(self, request):
        aws_req = AWSRequest.objects.filter(user=request.user).first()
        if aws_req:
            aws_req.status = STATUS_PENDING
        else:
            aws_req = AWSRequest(user=request.user)
        aws_req.save()
        return redirect('profile')


class ChangePWDView(LoginRequiredMixin, View):
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
            return redirect('user_password_change')
