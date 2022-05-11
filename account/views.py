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
from django.contrib.auth.views import PasswordChangeView
from django.core.mail import send_mail
import logging
from account.admin import register_IAM
from main.utils import get_current_user


# Create your views here

class LoginView(View):
    """
        View for user login with AWS credentials.
    """
    template_name = "account/login.html"

    def get(self, request):
        next_url = request.GET.get('next') if 'next' in request.GET else 'profile'
        if request.user.is_anonymous:
            form = UserLoginForm()
            return render(request, template_name=self.template_name, context={'form': form, "next": next_url})
        return redirect(next_url)

    def post(self, request):
        form = UserLoginForm(request.POST)
        #user = authenticate(aws_access_key=form.data['aws_access_key'],
        #                    aws_secret_access_key=form.data['aws_secret_access_key'])
        user = authenticate(email=form.data['email'],
                             password=form.data['password'])
        if user:
            login(request, user)
            
            if user.has_migrated_pwd:
            	next_url = request.POST.get('next') if 'next' in request.POST else 'profile'
            else:
            	next_url = '/password_reset/'
            return redirect(next_url)

        messages.error(request=request, message="Invalid Credentials, Try again!")
        return redirect('/')


class SignUpView(View):
    """
        View for user signup with email address.
    """
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
            logging.basicConfig(filename="email_log.txt",
                            filemode='a',
                            format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S",
                            level=logging.DEBUG)
            if user.email[-3:] == "edu":
                register_IAM("unused_arg", request, [user])
                try:
                    body_string = "This is an auto-generated email to let you know that " + user.email + " was just auto-approved for signup. This email is not confirmation that credential generation was successful, only that it is currently being attempted."
                    send_mail(
                        'SYSTEM: Auto-Generating for EDU user: ' + user.email,
                        body_string,
                        'neurocaas@gmail.com',
                        ['neurocaas@gmail.com'],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    logging.warning("SMTP Client failed:\n" + str(e))
            else:
                try:
                    body_string = "This is an auto-generated email to let you know that " + user.email + " just signed up for Neurocaas. This user was not auto-approved for signup, and can be approved manually on the admin page."
                    send_mail(
                        'SYSTEM: ' + user.email + ' is Pending Approval',
                        body_string,
                        'neurocaas@gmail.com',
                        ['neurocaas@gmail.com'],
                        fail_silently=False,
                    )
                except Exception as e:
                    pass
                    logging.warning("SMTP Client failed:\n" + str(e))
            messages.success(request, 'Successfully Registered, Please wait for email from us!')
            next_url = request.POST.get('next') if 'next' in request.POST else 'profile'
            return redirect(next_url)
            # return redirect('profile')

        return render(request, template_name=self.template_name, context={"form": form})


class ProfileView(LoginRequiredMixin, View):
    """
        View for viewing and updating a user's profile.
    """
    template_name = "account/profile.html"

    def get(self, request):
        aws_req = AWSRequest.objects.filter(user=request.user).first()
        iam = IAM.objects.filter(user=request.user).first()
        return render(request, template_name=self.template_name, context={
            "user": request.user,
            "aws_req": aws_req,
            'iam': IAM.objects.filter(user=request.user).first() if request.user.is_authenticated else None,
            'user': request.user if not request.user.is_anonymous else None,
            'logged_in': not request.user.is_anonymous
        })

    def post(self, request):
        form = ProfileChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Successfully updated!')

        return redirect('profile')


class AWSCredRequestView(LoginRequiredMixin, View):
    """
        AWS Credentials Request object View
     """
    def get(self, request):
        aws_req = AWSRequest.objects.filter(user=request.user).first()
        if aws_req:
            aws_req.status = STATUS_PENDING
        else:
            aws_req = AWSRequest(user=request.user)
        aws_req.save()
        return redirect('profile')


class ChangePWD2(LoginRequiredMixin, View):
    """
        View for changing users password, given old password and new password that meets django requirements. 
    """
    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, 'account/change_password.html', {
                'password_form': form,
        		'form': form,
                'iam': IAM.objects.filter(user=request.user).first() if request.user.is_authenticated else None,
                'user': request.user if not request.user.is_anonymous else None,
                'logged_in': not request.user.is_anonymous
        	}) 
    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.has_migrated_pwd = True
            user.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'There was an error processing your request.')
            return render(request, 'account/change_password.html', {
        		'password_form': form,
        		'form': form
        	}) 


class AdminMixin(UserPassesTestMixin):
    """
        Mixin for checking user admin status.
    """
    login_url = '/'

    def test_func(self):
        if self.request.user.is_anonymous:
            return False
        return self.request.user.is_admin


class IamCreateView(AdminMixin, View):
    """
        View for creating an IAM given an uploaded JSON file.
    """
    login_url = '/'

    def get(self, request):
        return render(request=request, template_name="account/iam_create.html", context={
            'iam': IAM.objects.filter(user=request.user).first() if request.user.is_authenticated else None
        })

    def post(self, request):
        errorg = ""
        if 'file' in request.FILES:
            file_content = request.FILES['file'].read().decode('utf-8')
            try:
                data = json.loads(file_content)
                email = data['email']
                password = data['password']
                username = data['username']
                access_key = data['accesskey']
                secret_access_key = data['secretaccesskey']
                group_name = data['groupname']

                # check if IAM is already existed or not
                if IAM.objects.filter(aws_user=username).count() > 0:
                    messages.error(request, f"IAM ( {username} ) is already existed.")
                    errorg = "?error=repeatusername"
                else:
                    # create new user with email
                    if User.objects.filter(email=email).count() > 0:
                        new_user = User.objects.filter(email=email).first()
                    else:
                        #new_user = User(email=email)
                        new_user = User.objects.create_user(email, password=password)
                        new_user.save()

                    if AWSRequest.objects.filter(user=new_user).count() == 0:
                        aws_req = AWSRequest(user=new_user)
                        aws_req.save()

                    if AnaGroup.objects.filter(name=group_name).count() > 0:
                        new_group = AnaGroup.objects.filter(name=group_name).first()
                    else:
                        new_group = AnaGroup(name=group_name)
                        new_group.save()

                    # create new iam with aws credentials
                    new_iam = IAM(user=new_user, aws_user=username, aws_access_key=access_key,
                                  aws_secret_access_key=secret_access_key, group=new_group)

                    new_iam.save()
                    messages.success(request, f"New IAM was successfully created: {username}")
                    return redirect('/admin/account/iam/')
            except Exception as e:
                messages.error(request, f"Issue: {e}")
                errorg = "?error=exception"
        else:
            messages.error(request, "File is empty. please upload json file")
            errorg = "?error=emptyfile"

        return redirect('/iamcreate/' + errorg)
