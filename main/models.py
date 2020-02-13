from django.db import models
from account.models import Base
# Create your models here.


class File(Base):
    name = models.CharField(max_length=100, null=False, blank=False, help_text='File Name')
    link = models.CharField(max_length=100, null=False, blank=False, help_text='Link of S3 bucket')
    bucket = models.CharField(max_length=100, null=False, blank=False, help_text='S3 Bucket name')

