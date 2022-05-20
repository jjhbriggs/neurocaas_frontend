from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from datetime import datetime
from .managers import UserManager

from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# Create your models here.
import random
import string
import uuid
import datetime as dt
class Base(models.Model):
    """
    Base Class which other Models inherit from.

    Contains timestamp information about the model.
    """
    #: Date/time when record was created.
    created_on = models.DateTimeField(auto_now_add=True, db_index=True,
                                      help_text='(Read-only) Date/time when record was created.')
    #: Date/time when record was updated.
    updated_on = models.DateTimeField(auto_now=True, db_index=True,
                                      help_text='(Read-only) Date/time when record was updated.')
    def save(self, *args, **kwargs):
        """Overriden save function to change 'updated_on' to reflect proper update time"""
        if self.pk is not None:
            self.updated_on = datetime.utcnow()
        super(Base, self).save(*args, **kwargs)
    class Meta:
        abstract = True