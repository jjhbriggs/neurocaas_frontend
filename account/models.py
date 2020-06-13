from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from datetime import datetime
from .managers import UserManager


# Create your models here.


class Base(models.Model):
    """
    Base Class which other Models inherit from.

    Contains timestamp information about actions.
    """
    #: The time when the model was created
    created_on = models.DateTimeField(auto_now_add=True, db_index=True,
                                      help_text='(Read-only) Date/time when record was created.')
    #: The time when the model was last updated
    updated_on = models.DateTimeField(auto_now=True, db_index=True,
                                      help_text='(Read-only) Date/time when record was updated.')
    #: Overriden save function to change 'updated_on' to reflect proper update time
    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.updated_on = datetime.utcnow()
        super(Base, self).save(*args, **kwargs)
    class Meta:
        abstract = True


STATUS_PENDING = 'P'
STATUS_COMPLETED = 'C'
STATUS_DENIED = 'D'


class User(AbstractBaseUser):
    objects = UserManager()
    date_added = models.DateField(auto_now=False, auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    email = models.EmailField(db_index=True, unique=True)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False, help_text="Flag for administrator account")
    data_transfer_permission = models.BooleanField(default=True,
                                                   help_text="Permission for individual users access to data transfer")

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + " " + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.email

    def is_staff(self):
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def has_perm(self, perm, obj=None):
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        # Simplest possible answer: Yes, always
        return True


class AnaGroup(Base):
    name = models.CharField(max_length=50, help_text='Group Name', unique=True)

    def __str__(self):
        return self.name


class IAM(Base):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    aws_user = models.CharField(max_length=155, help_text="AWS account username")
    aws_access_key = models.CharField(max_length=255, help_text="AWS Access key id", unique=True)
    aws_secret_access_key = models.CharField(max_length=255, help_text="AWS Secret key")
    group = models.ForeignKey(AnaGroup, on_delete=models.CASCADE)
    # group = models.CharField(max_length=255, help_text='Group Name', default='bendeskylab')

    def __str__(self):
        return self.aws_user

    def save(self, *args, **kwargs):
        aws_req = AWSRequest.objects.filter(user=self.user).first()
        if aws_req:
            aws_req.status = STATUS_COMPLETED
            aws_req.save()
        super(IAM, self).save(*args, **kwargs)


class AWSRequest(Base):
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_DENIED, 'Denied'),
        (STATUS_COMPLETED, 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING,
                              help_text="Status of request")

    def __str__(self):
        return self.user.email

