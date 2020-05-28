from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Analysis)
class SubFolderAdmin(admin.ModelAdmin):
    list_display = ('analysis_name', 'bucket_name', 'short_description', 'custom')
