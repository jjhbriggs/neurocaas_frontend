from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Bucket)
class BucketAdmin(admin.ModelAdmin):
    list_display = ('name', 'algorithrm', 'description', 'created_on',)


@admin.register(FileItem)
class FileItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'link', 'uploaded', 'created_on',)


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ('name', 'iam', 's3_path', 'created_on',)


@admin.register(SubFolder)
class SubFolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'bucket', 'created_on', )


@admin.register(Config)
class SubFolderAdmin(admin.ModelAdmin):
    list_display = ('process_name', 'input_folder', 'result_prefix', 'bucket_name')
