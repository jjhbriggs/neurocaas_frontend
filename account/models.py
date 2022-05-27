from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from datetime import datetime
from .managers import UserManager

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.
from django.core.validators import RegexValidator
import random
import string
import uuid
import datetime as dt
from main.models import Analysis
from .base_model import Base

def group_uuid():
        return uuid.uuid4().hex.upper()[0:6]

class AnaGroup(Base):
    """
    AnaGroup model.

    All users belong to a group.
    """
    #: Name of the group.
    name = models.CharField(max_length=50, help_text='Group Name', unique=True)
    code = models.CharField(max_length=6,blank=False, default=group_uuid)
    analyses = models.ManyToManyField(Analysis, blank=True)
    
    
    #: Returns name of the group.
    def __str__(self):
        return self.name
    #: makes a uuid
   
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

class User(AbstractBaseUser):
    """
    Basic User model.

    Contains basic user information such as email, name, admin rights, etc.
    A new user is created every time someone signs up using their email through the website.
    """
    objects = UserManager()
    #: Date when user was added.
    date_added = models.DateField(auto_now=False, auto_now_add=True)
    #: Time when user was added. Note: seperate from date_added due to dev process. Originally date_added was unused, however has since seen use as an indentifier for iam credentials. However daily is not specific enough, so time was added, but existing identifiers used day only. 
    time_added = models.TimeField(default=dt.time.min, blank=True)
    #: Date/time when user was updated.
    date_updated = models.DateField(auto_now=True)
    #: Email associated with the user. Users are identified by this email address.
    email = models.EmailField(db_index=True, unique=True)
    #: First Name of User.
    first_name = models.CharField(max_length=100, default="", blank=True)
    #: Last Name of User.
    last_name = models.CharField(max_length=100, default="", blank=True)
        
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')

    #unique=True,
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    #: Boolean value checking if the account is active. 
    is_active = models.BooleanField(default=True)
    #: Boolean value checking if the account is an admin.
    is_admin = models.BooleanField(default=False, help_text="Flag for administrator account")
    is_staff = models.BooleanField(default=False, help_text="Flag for administrator account")
    is_superuser = models.BooleanField(default=False, help_text="Flag for administrator account")
    #: Boolean value checking for permission for individual users access to data transfer.
    #data_transfer_permission = models.BooleanField(default=True,
    #                                               help_text="Permission for individual users access to data transfer")
    def get_full_name(self):
        """Returns first and last name of user."""
        # The user is identified by their email address
        if self.first_name  == "" and self.last_name == "": 
             return self.email
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        """Returns email of user."""
        # The user is identified by their email address
        return self.email

    def __str__(self):
        """Returns email of user."""
        return self.email

    def has_perm(self, perm, obj=None):
        """Returns True. """
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Returns True. """
        # Simplest possible answer: Yes, always
        return True

class IAM(Base):
    """
    IAM model which is associated with a user.

    Each IAM model contains basic AWS IAM information such as username, access key, and secret access key of the IAM account.
    """
    #: The User this IAM is associated with.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #: AWS account username.
    aws_user = models.CharField(max_length=155, help_text="AWS account username", blank=True, null=True)
    #: AWS access key
    aws_access_key = models.CharField(max_length=255, help_text="AWS Access key id")
    #: AWS secret access key
    aws_secret_access_key = models.CharField(max_length=255, help_text="AWS Secret key")

    aws_session_token = models.CharField(max_length=255, help_text="AWS session token")
    #: The group this IAM is associated with
    group = models.ForeignKey(AnaGroup, on_delete=models.CASCADE)
    # group = models.CharField(max_length=255, help_text='Group Name', default='bendeskylab')
    #aws_pwd = models.CharField(max_length=255, help_text="AWS account password")
    cred_expire = models.DateTimeField(null=True,blank=True,help_text='Time Temporary Credentials Expire',)

    fixed_creds = models.BooleanField(default=False,help_text='User Gets Permanent Credentials',)

    def __str__(self):
        """Returns AWS IAM Username."""
        return self.user.email
    class Meta:
        verbose_name = 'IAM'
        verbose_name_plural = 'IAMs'