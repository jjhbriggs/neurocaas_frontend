from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .forms import *
from .models import *
import time
#from subprocess import Popen, PIPE
import subprocess
import json
import os
import sys
from django.contrib import messages
import getpass

# Register your models here.
user_profiles = "/home/ubuntu/ncap/neurocaas/ncap_iac/user_profiles"
#: Registers IAM Automatically with AWS and the Django DB
def register_IAM(modeladmin, request, queryset):
    current_p = 0
    #: Register IAM for every user in query
    for usr in queryset:  
        #: Check that the user doesn't have an IAM already
        if len(IAM.objects.filter(user=usr)) == 0:
            if usr.requested_group_name == "":
                messages.error(request, "System error, requested group name blank")
                continue
            #: Check for existing IAM group in resources for cloudformation
            group_exists = os.path.isdir(os.path.join(user_profiles, 'group-' + str(usr.requested_group_name)))
            #: Generate one if there isn't an existing folder
            if not group_exists:
                command = 'source ~/ncap/venv/bin/activate && cd ~/ncap/neurocaas/ncap_iac/user_profiles/iac_utils && bash ' + str(os.path.join(user_profiles, 'iac_utils/configure.sh')) + ' group-' + str(usr.requested_group_name)
                '''process = subprocess.Popen([command],
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE,
                            shell=True)
                stdout, stderr = process.communicate()'''
                outfile = open('logs/iam_creation_out_log_1.txt','w')
                errfile = open('logs/iam_creation_err_log_1.txt','w')

                process = subprocess.Popen([command],
                                stdout=outfile, 
                                stderr=errfile,
                                shell=True, 
                                executable='/bin/bash')
                process.communicate()
            user_config_array = {}
            #: Fill correct JSON data for cloudformation
            with open(os.path.join(user_profiles, 'group-' + str(usr.requested_group_name), 'user_config_template.json')) as f:
                user_config_array = json.load(f)
                affiliate = user_config_array['UXData']["Affiliates"][0]
                if (not usr.email[0:15].replace('@', '').split('.', 1)[0] in affiliate["UserNames"]) and (not usr.email in affiliate["ContactEmail"]):
                    if not group_exists:
                        affiliate["AffiliateName"] = usr.requested_group_name
                        affiliate["UserNames"] = [usr.email[0:25].replace('@', '').split('.', 1)[0]]
                        affiliate["ContactEmail"] = [usr.email]
                    else:
                        affiliate["UserNames"].append(usr.email[0:25].replace('@', '').split('.', 1)[0])
                        affiliate["ContactEmail"].append(usr.email)
                user_config_array['UXData']["Affiliates"][0] = affiliate
            with open(os.path.join(user_profiles, 'group-' + str(usr.requested_group_name), 'user_config_template.json'), 'w') as outfile:
                json.dump(user_config_array, outfile)
            #: Call deploy.sh script to deploy these resources
            command = 'source ~/ncap/venv/bin/activate && source activate /home/ubuntu/ncap/neurocaas && cd ~/ncap/neurocaas/ncap_iac/user_profiles/iac_utils && ./deploy.sh ' + os.path.join(user_profiles,'group-' + str(usr.requested_group_name) + ' &')
            outfile = open('logs/iam_creation_out_log.txt','w')
            errfile = open('logs/iam_creation_err_log.txt','w')

            process = subprocess.Popen([command],
                            stdout=outfile, 
                            stderr=errfile,
                            shell=True, 
                            executable='/bin/bash')
            process.communicate()
            messages.add_message(request, messages.INFO, "The IAM Creation Process has started. Please check back later to see if your resources have been created.")
            current_p = current_p + 1
        else:
            messages.error(request, "A User with an existing IAM was selected")
register_IAM.short_description = "Generate an IAM and Group for this user in django db and cloudformation"
#: Removes IAM Automatically with AWS and the Django DB
def remove_IAM(modeladmin, request, queryset):
    current_p = 0
    #: Remove IAM for every user in query
    for usr in queryset:  
        #: Check that the user has an IAM already
        if len(IAM.objects.filter(user=usr)) > 0:
            user_config_array = {}
            current_iam = IAM.objects.filter(user=usr).first()
            current_group = current_iam.group
            #: Remove correct JSON data for cloudformation
            with open(os.path.join(user_profiles, 'group-' + str(current_group), 'user_config_template.json')) as f:
                user_config_array = json.load(f)
                affiliate = user_config_array['UXData']["Affiliates"][0]
                curren_un = current_iam.aws_user.replace(user_config_array['Lambda']['LambdaConfig']['REGION'],'')
                if (curren_un in affiliate["UserNames"]) and (usr.email in affiliate["ContactEmail"]):
                    #: Then IAM exists in the data, and you can Remove the IAM 
                    affiliate["UserNames"].remove(curren_un)
                    affiliate["ContactEmail"].remove(usr.email)
                user_config_array['UXData']["Affiliates"][0] = affiliate
            with open(os.path.join(user_profiles, 'group-' + str(current_group), 'user_config_template.json'), 'w') as outfile:
                json.dump(user_config_array, outfile)
            #: Call deploy.sh script to deploy these resources
            command = 'source ~/ncap/venv/bin/activate && cd ~/ncap/neurocaas/ncap_iac/user_profiles/iac_utils && ./deploy.sh ' + os.path.join(user_profiles,'group-' + str(current_group) + ' &')
            outfile = open('logs/iam_removal_out_log.txt','w')
            errfile = open('logs/iam_removal_err_log.txt','w')
            process = subprocess.Popen([command],
                            stdout=outfile, 
                            stderr=errfile,
                            shell=True, 
                            executable='/bin/bash')
            process.communicate()
            messages.add_message(request, messages.INFO, "The IAM Removal Process has started. Please check back later to see if your resources have been removed.")
            current_p = current_p + 1
            #: Remove IAM from django db
            current_iam.delete()
        else:
            messages.error(request, "A user was selected that did not contain a valid IAM")
remove_IAM.short_description = "Remove associated IAM from cloudformation stacks and django db"


class UserAdministrator(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm

    list_display = ('email', 'is_admin', "has_IAM_attached", 'has_migrated_pwd', 'first_name', 'last_name', 'use_code', 'requested_group_name', 'requested_group_code',)
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'has_migrated_pwd', 'first_name', 'last_name', 'use_code', 'requested_group_name', 'requested_group_code')}),
        ('Permissions', {'fields': ('data_transfer_permission',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'has_migrated_pwd', 'first_name', 'last_name', 'data_transfer_permission','use_code','requested_group_name','requested_group_code',)}
         ),
    )
    actions = [register_IAM, remove_IAM]
    def has_IAM_attached(self, obj):
        if len(IAM.objects.filter(user=obj)) == 1:
            return True
        return False
    has_IAM_attached.boolean = True

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()



@admin.register(IAM)
class IAMAdmin(admin.ModelAdmin):
    list_display = ('user', 'aws_user', 'aws_access_key', 'aws_pwd', 'group', 'created_on')
    readonly_fields = ['group']


@admin.register(AWSRequest)
class AWSAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_on')


@admin.register(AnaGroup)
class AWSAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_on')
    readonly_fields=('code',)

admin.site.register(User, UserAdministrator)
admin.site.unregister(Group)
# admin.site.register(IAM)
# admin.site.register(AWSRequest)
