from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .managers import UserManager

# Create your models here.


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
    is_admin = models.BooleanField(default=False)

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


class IAM(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    aws_user = models.CharField(max_length=155)
    aws_access_key = models.CharField(max_length=255)
    aws_secret_access_key = models.CharField(max_length=255)

    def __str__(self):
        return self.username
