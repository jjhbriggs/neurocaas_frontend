from django.db import models
# Create your models here.
from datetime import datetime
from account.models import Base
import uuid


class Bucket(Base):
    name = models.CharField(max_length=100, null=False, blank=False, help_text='Bucket name')
    description = models.TextField(blank=True, null=True, help_text="Description of bucket")
    algorithrm = models.CharField(max_length=100, null=True, blank=True, help_text='Algorithm name')

    def __str__(self):
        return self.name


STATUS_PENDING = 'P'
STATUS_COMPLETED = 'C'
STATUS_FAILED = 'F'


def rand_id():
    return str(uuid.uuid1())


class SubFolder(Base):
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, help_text="bucket")
    name = models.CharField(max_length=100, default=rand_id, help_text='Subfolder name {Random Field}', unique=True)

    def __str__(self):
        return self.name


class FileItem(Base):
    name = models.CharField(max_length=100, null=False, blank=False, help_text='File Name')
    link = models.CharField(max_length=100, null=False, blank=False, help_text='Link of S3 bucket')
    uploaded = models.BooleanField(default=False, help_text="Flag to show complete of uploading")
    bucket = models.ForeignKey(Bucket, on_delete=models.CASCADE, help_text="Bucket of file")

    def __str__(self):
        return self.name


class Process(Base):
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_COMPLETED, 'Completed'),
    )

    name = models.CharField(max_length=100, default=rand_id, help_text='Process name {Random Field}', unique=True)
    iam = models.ForeignKey("account.IAM", on_delete=models.CASCADE, help_text="User IAM for process")
    subfolder = models.ForeignKey(SubFolder, on_delete=models.CASCADE, help_text='Subfolder of files',
                                  null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=STATUS_PENDING,
                              help_text="Status of process")

    uploaded_file = models.ForeignKey(FileItem, on_delete=models.CASCADE, help_text="Uploaded json file")
    s3_path = models.CharField(max_length=200, null=True, blank=True, help_text="Result path of s3")
    local_file = models.CharField(max_length=200, null=True, blank=True, help_text="Result file of server")

    def __str__(self):
        return self.name


class Analysis(Base):
    analysis_name = models.CharField(max_length=100, help_text='Name of Process', unique=True)
    upload_folder = models.CharField(max_length=100, help_text='Folder to upload dataset and config items',
                                     null=True, blank=True)
    result_prefix = models.CharField(max_length=100, help_text='Prefix of result folder name')
    result_items = models.TextField(help_text='Json of result files')
    bucket_name = models.CharField(max_length=100, help_text='Bucket Name')
    result_path = models.CharField(max_length=100, blank=True, null=True, help_text='Path of results')
    config_path = models.CharField(max_length=100, blank=True, null=True, help_text='Path of config file')
    dataset_path = models.CharField(max_length=100, blank=True, null=True, help_text='Path of dataset files')
    submit_path = models.CharField(max_length=100, blank=True, null=True, help_text='Path of submit file')

    # detail fields of analysis
    short_description = models.TextField(help_text='Short description of analysis', blank=True, null=True)
    long_description = models.TextField(help_text='Long description of analysis', blank=True, null=True)

    paper_link = models.CharField(max_length=100, help_text='Link of Analysis Paper', blank=True, null=True)
    git_link = models.CharField(max_length=100, help_text='Github link of Analysis', blank=True, null=True)
    bash_link = models.CharField(max_length=100, help_text='Bash script link of Analysis', blank=True, null=True)
    signature = models.TextField(help_text='Signature of analysis', blank=True, null=True)

    def __str__(self):
        return self.analysis_name