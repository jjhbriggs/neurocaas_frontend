from django.db import models
# Create your models here.
from datetime import datetime
from account.models import Base, AnaGroup
import uuid


def rand_id():
    return str(uuid.uuid1())


class Analysis(Base):
    """Analysis Model. Contains specific analysis options and details."""
    
    #: Name of Process.
    analysis_name = models.CharField(max_length=100, help_text='Name of Process', unique=True)
    #: Prefix of result folder name.
    result_prefix = models.CharField(max_length=100, help_text='Prefix of result folder name')
    #: S3 Bucket Name.
    bucket_name = models.CharField(max_length=100, help_text='Bucket Name')
    #: Custom Analysis option.
    custom = models.BooleanField(help_text='Custom Analysis option', default=False)
    #: Groups with access to use this analysis.
    groups = models.ManyToManyField(AnaGroup)

    # detail fields of analysis
    #: Short description of analysis.
    short_description = models.TextField(help_text='Short description of analysis', blank=True, null=True)
    #: Long description of analysis.
    long_description = models.TextField(help_text='Long description of analysis', blank=True, null=True)
    #: Link of Analysis Paper.
    paper_link = models.CharField(max_length=100, help_text='Link of Analysis Paper', blank=True, null=True)
    #: Github link of Analysis.
    git_link = models.CharField(max_length=100, help_text='Github link of Analysis', blank=True, null=True)
    #: Bash script link of Analysis.
    bash_link = models.CharField(max_length=100, help_text='Bash script link of Analysis', blank=True, null=True)
    #: Link of Demo page.
    demo_link = models.CharField(max_length=100, help_text='Link of Demo page', blank=True, null=True)
    #: Signature of analysis.
    signature = models.TextField(help_text='Signature of analysis', blank=True, null=True)

    def __str__(self):
        """Returns analysis name."""
        return self.analysis_name

    def check_iam(self, iam):
        """Check's if the user's IAM Group has permission to access this analysis"""
        for group in self.groups.all():
            if iam.group == group:
                return True
        return False

    class Meta:
        verbose_name_plural = "Analyses"
