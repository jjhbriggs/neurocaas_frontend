from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class IAM(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=155)
    access_key = models.CharField(max_length=255)
    secret_access_key = models.CharField(max_length=255)

    def __str__(self):
        return self.username

