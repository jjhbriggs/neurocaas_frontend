from django import forms
from .models import User, IAM, AnaGroup
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .managers import UserManager
import time
import subprocess
import json
import os
import sys
from django.contrib import messages
from datetime import datetime
from main.utils import groupname_from_user

'''
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model


class RegisterForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')
'''



class UserCreationForm(forms.ModelForm):
    """UserCreationForm()
    A form for creating new users with the given information."""

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    #: Email associated with the user. Users are identified by this email address. [Jflag repet w/ meta?]
    email = forms.CharField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control'}))

    use_code = forms.BooleanField(label='Use Group Code', required=False)
    
    group_code = forms.CharField(label='Group Code', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        """The Meta class creates form fields from model fields. 
        In this case the model being used is :class:`~account.models.User`, and the user's :attr:`~account.models.User.email`
        field is being used."""
        model = User
        #fields = ('email', 'first_name', 'last_name')
        #: Fields used.
        fields = ('email',)

    def clean_password2(self):
        """A function to check that the two passwords provided by the user match."""
        # Check that the two password entries match
        #: User's password.
        password1 = self.cleaned_data.get("password1")
        #: Password confirm.
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The passwords must match.")
        return password2
    def clean_group_code(self):
        """Checks that the entered group code matches a group"""

        code = self.cleaned_data.get("group_code")
        if self.cleaned_data.get("use_code") == True and len(AnaGroup.objects.filter(code=code)) == 0:
            raise forms.ValidationError("Your join group code is wrong. Make sure you are using only capital letters and numbers")
        return code

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.clean_password2())
        user.time_added = datetime.now().time()
        if commit:
            user.save()
            if self.cleaned_data.get("use_code"):
                new_group = AnaGroup.objects.filter(code=self.clean_group_code()).first()
            else:
                new_group = AnaGroup.objects.create(name=groupname_from_user(user))
            new_group.save()
            iam = IAM.objects.create(user=user,
                            aws_access_key="No creds yet",
                            aws_secret_access_key="No creds yet",
                            aws_session_token = 'No token yet',
                            group=new_group)
            iam.save()
        #user.requested_group_name = user.email.replace('@', '').replace('.', '').replace('_', '-')[0:12] + str(int(round(time.time())))
        #user.requested_group_code = self.clean_group_code()
        # group_search = AnaGroup.objects.filter(name=user.requested_group_name)
        # if len(list(group_search))==0:
        #     user.group = AnaGroup.objects.create(name=user.requested_group_name)
        # else:
        #     user.group = group_search[0]
        return user



class UserLoginForm(forms.ModelForm):
    """UserLoginForm()
    A form for user login using aws credentials."""

    class Meta:
        """The Meta class creates form fields from model fields. 
        In this case the model being used is :class:`~account.models.IAM`, and the user's 
        :attr:`~account.models.IAM.aws_access_key` and :attr:`~account.models.IAM.aws_secret_access_key`
        fields are being used."""
        model = User
        #: Fields used.
        fields = ('email', 'password',)
    #: AWS access key. [Jflag repet w/ meta?]
    email = forms.CharField(label='Email', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'id': 'email',
            'type': 'text'
        }
    ))
    #: AWS secret access key. [Jflag repet w/ meta?]
    password = forms.CharField(label='Password', widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'id': 'password',
        }
    ))


class ProfileChangeForm(forms.ModelForm):
    """ProfileChangeForm()
    A form for changing a user's name."""

    class Meta:
        """The Meta class creates form fields from model fields. 
        In this case the model being used is :class:`~account.models.User`, and the user's 
        :attr:`~account.models.User.first_name` and :attr:`~account.models.User.last_name` fields are being used."""
        model = User
        #: Fields used.
        fields = ('first_name', 'last_name',)
