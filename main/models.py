from django.db import models
# Create your models here.
from datetime import datetime
from account.models import Base, AnaGroup
import uuid


def rand_id():
    return str(uuid.uuid1())


class Analysis(Base):
    analysis_name = models.CharField(max_length=100, help_text='Name of Process', unique=True)
    result_prefix = models.CharField(max_length=100, help_text='Prefix of result folder name')
    bucket_name = models.CharField(max_length=100, help_text='Bucket Name')
    groups = models.ManyToManyField(AnaGroup)

    # detail fields of analysis
    short_description = models.TextField(help_text='Short description of analysis', blank=True, null=True)
    long_description = models.TextField(help_text='Long description of analysis', blank=True, null=True)

    paper_link = models.CharField(max_length=100, help_text='Link of Analysis Paper', blank=True, null=True)
    git_link = models.CharField(max_length=100, help_text='Github link of Analysis', blank=True, null=True)
    bash_link = models.CharField(max_length=100, help_text='Bash script link of Analysis', blank=True, null=True)
    demo_link = models.TextField(help_text='Link of Demo page', blank=True, null=True)
    signature = models.TextField(help_text='Signature of analysis', blank=True, null=True)

    def __str__(self):
        return self.analysis_name

    def check_iam(self, iam):
        for group in self.groups.all():
            if iam.group == group:
                return True
        return False
