from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import View
from .models import *
from .forms import *
from ncap.backends import authenticate
import json
from django.contrib import messages


# Create your views here.

class LoginView(View):
    template_name = "account/login.html"

    def get(self, request):
        next_url = request.GET.get('next') if 'next' in request.GET else 'profile'
        if request.user.is_anonymous:
            form = UserLoginForm()
            return render(request, template_name=self.template_name, context={'form': form, "next": next_url})
        return redirect(next_url)

    def post(self, request):
        form = UserLoginForm(request.POST)
        user = authenticate(aws_access_key=form.data['aws_access_key'],
                            aws_secret_access_key=form.data['aws_secret_access_key'])

        if user:
            login(request, user)
            next_url = request.POST.get('next') if 'next' in request.POST else 'profile'
            return redirect(next_url)

        messages.error(request=request, message="Invalid Credentials, Try again!")
        return redirect('/')


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
            next_url = request.POST.get('next') if 'next' in request.POST else 'profile'
            return redirect(next_url)
            # return redirect('profile')

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


class AdminMixin(UserPassesTestMixin):
    login_url = '/'

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        return self.request.user.is_admin


class IamCreateView(AdminMixin, View):
    login_url = '/'

    def get(self, request):
        return render(request=request, template_name="account/iam_create.html", context={
            'iam': IAM.objects.filter(user=request.user).first() if request.user.is_authenticated else None
        })

    def post(self, request):
        if 'file' in request.FILES:
            file_content = request.FILES['file'].read().decode('utf-8')
            try:
                data = json.loads(file_content)
                email = data['email']
                username = data['username']
                access_key = data['accesskey']
                secret_access_key = data['secretaccesskey']
                group_name = data['groupname']

                # check if IAM is already existed or not
                if IAM.objects.filter(aws_user=username).count() > 0:
                    messages.error(request, f"IAM ( {username} ) is already existed.")
                else:
                    # create new user with email
                    if User.objects.filter(email=email).count() > 0:
                        new_user = User.objects.filter(email=email).first()
                    else:
                        new_user = User(email=email)
                        new_user.save()

                    # create new iam with aws credentials
                    new_iam = IAM(user=new_user, aws_user=username, aws_access_key=access_key,
                                  aws_secret_access_key=secret_access_key, group=group_name)
                    new_iam.save()
                    messages.success(request, f"New IAM was successfully created: {username}")
                    return redirect('/admin/account/iam/')
            except Exception as e:
                messages.error(request, f"Issue: {e}")
        else:
            messages.error(request, "File is empty. please upload json file")

        return redirect('/iamcreate/')
