from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_on',)


@admin.register(FileItem)
class FileItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'uploaded',)
