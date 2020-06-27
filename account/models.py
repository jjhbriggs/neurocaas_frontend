from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from datetime import datetime
from .managers import UserManager

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Base(models.Model):
    """
    Base Class which other Models inherit from.

    Contains timestamp information about the model.
    """
    #: Date/time when record was created.
    created_on = models.DateTimeField(auto_now_add=True, db_index=True,
                                      help_text='(Read-only) Date/time when record was created.')
    #: Date/time when record was updated.
    updated_on = models.DateTimeField(auto_now=True, db_index=True,
                                      help_text='(Read-only) Date/time when record was updated.')
    def save(self, *args, **kwargs):
        """Overriden save function to change 'updated_on' to reflect proper update time"""
        if self.pk is not None:
            self.updated_on = datetime.utcnow()
        super(Base, self).save(*args, **kwargs)
    class Meta:
        abstract = True


STATUS_PENDING = 'P'
STATUS_COMPLETED = 'C'
STATUS_DENIED = 'D'


'''
class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=140, default=email)
	#: First Name of User.
    first_name = models.CharField(max_length=100, default="")
    #: Last Name of User.
    last_name = models.CharField(max_length=100, default="")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    #: Boolean value checking if the account is active. [JFlag]
    is_active = models.BooleanField(default=True)
    #: Boolean value checking if the account is an admin.
    is_admin = models.BooleanField(default=False, help_text="Flag for administrator account")
    #: Boolean value checking for permission for individual users access to data transfer.
    data_transfer_permission = models.BooleanField(default=True,
                                                   help_text="Permission for individual users access to data transfer")
'''
class User(AbstractBaseUser):
    """
    Basic User model.

    Contains basic user information such as email, name, admin rights, etc.
    A new user is created every time someone signs up using their email through the website.
    """
    objects = UserManager()
    #: Date/time when user was added.
    date_added = models.DateField(auto_now=False, auto_now_add=True)
    #: Date/time when user was updated.
    date_updated = models.DateField(auto_now=True)
    #: Email associated with the user. Users are identified by this email address.
    email = models.EmailField(db_index=True, unique=True)
    #: First Name of User.
    first_name = models.CharField(max_length=100, default="")
    #: Last Name of User.
    last_name = models.CharField(max_length=100, default="")
    
    has_migrated_pwd = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    #: Boolean value checking if the account is active. [JFlag]
    is_active = models.BooleanField(default=True)
    #: Boolean value checking if the account is an admin.
    is_admin = models.BooleanField(default=False, help_text="Flag for administrator account")
    #: Boolean value checking for permission for individual users access to data transfer.
    data_transfer_permission = models.BooleanField(default=True,
                                                   help_text="Permission for individual users access to data transfer")

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

    def is_staff(self):
        """Returns true if user is an admin."""
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def has_perm(self, perm, obj=None):
        """Returns True. [Jflag]"""
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        """Returns True. [Jflag]"""
        # Simplest possible answer: Yes, always
        return True

class AnaGroup(Base):
    """
    AnaGroup model.

    All users belong to a group.
    """
    #: Name of the group.
    name = models.CharField(max_length=50, help_text='Group Name', unique=True)
    
    #: Returns name of the group.
    def __str__(self):
        return self.name


class IAM(Base):
    """
    IAM model which is associated with a user.

    Each IAM model contains basic AWS IAM information such as username, access key, and secret access key of the IAM account.
    """
    #: The User this IAM is associated with.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #: AWS account username.
    aws_user = models.CharField(max_length=155, help_text="AWS account username")
    #: AWS access key
    aws_access_key = models.CharField(max_length=255, help_text="AWS Access key id", unique=True)
    #: AWS secret access key
    aws_secret_access_key = models.CharField(max_length=255, help_text="AWS Secret key")
    #: The group this IAM is associated with
    group = models.ForeignKey(AnaGroup, on_delete=models.CASCADE)
    # group = models.CharField(max_length=255, help_text='Group Name', default='bendeskylab')

    def __str__(self):
        """Returns AWS IAM Username."""
        return self.aws_user

    def save(self, *args, **kwargs):
        """Overriden save function to update the AWSRequest class associated with this IAM user. 
        Changes the AWSRequest status to 'Completed.'"""
        aws_req = AWSRequest.objects.filter(user=self.user).first()
        if aws_req:
            aws_req.status = STATUS_COMPLETED
            aws_req.save()
        super(IAM, self).save(*args, **kwargs)


class AWSRequest(Base):
    """
    AWSRequest class which holds basic information about the status of a user account.

    A user can have a status of 'Pending,' 'Completed,' or 'Denied,' depending on the approval status of their account
    """
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_DENIED, 'Denied'),
        (STATUS_COMPLETED, 'Completed'),
    )
    #: The user which this AWSRequest is associated with.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #: The status of this user's account. ('Pending,' 'Completed,' or 'Denied')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING,
                              help_text="Status of request")

    def __str__(self):
        """Returns the email of the account associated with this AWSRequest"""
        return self.user.email

