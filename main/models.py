from django.db import models
# Create your models here.
from datetime import datetime
from account.models import Base


class Bucket(Base):
    name = models.CharField(max_length=100, null=False, blank=False, help_text='Bucket name')
    description = models.TextField(blank=True, null=True, help_text="Description of bucket")

    def __str__(self):
        return self.name


class FileItem(Base):
    iam = models.ForeignKey("account.IAM", on_delete=models.CASCADE, help_text='User of s3 bucket')
    name = models.CharField(max_length=100, null=False, blank=False, help_text='File Name')
    link = models.CharField(max_length=100, null=False, blank=False, help_text='Link of S3 bucket')
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, related_name='bucket_name')
    size = models.BigIntegerField(default=0, help_text="The size of file")
    uploaded = models.BooleanField(default=False, help_text="Flag to show complete of uploading")
    sub_folder = models.CharField(max_length=100, null=False, blank=False, help_text='Sub folder inside bucket')

    def __str__(self):
        return self.name


class Process(Base):

    pass



