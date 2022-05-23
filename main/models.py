from django.db import models
# Create your models here.
from datetime import datetime
from account.base_model import Base
import uuid
from django.core.validators import RegexValidator

class ConfigTemplate(Base):
    """
    ConfigTemplate model.

    Allows for embedding configuration files 
    """
    config_name = models.CharField(max_length=100, help_text='Name of Process', unique=True, default="default")
    orig_yaml = models.TextField(help_text='Sample yaml config file (leave sample values entered)', blank=True, null=True)

    def __str__(self):
        """Returns config name."""
        return self.config_name
class Analysis(Base):
    """Analysis Model. Contains specific analysis options and details."""
    
    prefix_validator = RegexValidator(r'^job__.+_$', 'Input needs to match format job__bucketname_.')

    #: Name of Process.
    analysis_name = models.CharField(max_length=100, help_text='Name of Process', unique=True)
    #: Prefix of result folder name.
    result_prefix = models.CharField(max_length=100, help_text='Prefix of result folder name. FORMAT: job__bucketName_', validators=[prefix_validator])
    #: S3 Bucket Name.
    bucket_name = models.CharField(max_length=100, help_text='Bucket Name')
    
    #: Custom Analysis option.
    custom = models.BooleanField(help_text='Custom Analysis option', default=False)
    #: Groups with access to use this analysis.
    groups_TOBEDELETED = models.ManyToManyField('account.AnaGroup') #renamed temporarily so that data persists but anything referencing it will break.

    config_template = models.ForeignKey(ConfigTemplate, on_delete=models.CASCADE, blank=True, null=True)

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
        # for group in self.groups.all():
        #     if iam.group == group:
        #         return True
        return False

    class Meta:
        verbose_name_plural = "Analyses"
