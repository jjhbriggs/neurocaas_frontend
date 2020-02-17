from django.db import models
# Create your models here.
from datetime import datetime
from account.models import Base
import uuid


class Bucket(Base):
    name = models.CharField(max_length=100, null=False, blank=False, help_text='Bucket name')
    description = models.TextField(blank=True, null=True, help_text="Description of bucket")
    algorithrm = models.CharField(max_length=100, null=False, blank=False, help_text='Algorithm name')

    def __str__(self):
        return self.name


STATUS_PENDING = 'P'
STATUS_COMPLETED = 'C'
STATUS_FAILED = 'F'


def rand_id():
    return str(uuid.uuid1())


class Process(Base):
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_COMPLETED, 'Completed'),
    )
    iam = models.ForeignKey("account.IAM", on_delete=models.CASCADE, help_text="User IAM for process")
    name = models.CharField(max_length=100, default=rand_id, help_text='Process name {Random Field}', unique=True)
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, help_text='Bucket of files')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING,
                              help_text="Status of process")


class FileItem(Base):
    iam = models.ForeignKey("account.IAM", on_delete=models.CASCADE, help_text='User of s3 bucket')
    name = models.CharField(max_length=100, null=False, blank=False, help_text='File Name')
    link = models.CharField(max_length=100, null=False, blank=False, help_text='Link of S3 bucket')
    process = models.ForeignKey(Process, on_delete=models.CASCADE, help_text='Process')
    size = models.BigIntegerField(default=0, help_text="The size of file")
    uploaded = models.BooleanField(default=False, help_text="Flag to show complete of uploading")

    def __str__(self):
        return self.name

