import os
import json
import subprocess
from datetime import datetime

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import *
from .models import *
from main.models import *

# Register your models here.
user_profiles = "/home/ubuntu/ncap/neurocaas/ncap_iac/user_profiles"
#: Registers IAM Automatically with AWS and the Django DB
def make_username(usr):
    """
        'Make' a username from the users email and time of creation.
        Will always make the same username when called on the same user.
    """
    _timestamp = int(datetime.combine(usr.date_added, usr.time_added).timestamp())
    username = ""
    dot_chunks = usr.email.replace('@', '').split('.')

    for index,chunk in enumerate(dot_chunks):
        if index != len(dot_chunks) - 1:
            username += chunk
    username = username[0:12] + str(_timestamp)
    return username
def register_IAM(modeladmin, request, queryset): # pragma: no cover
    #: Register IAM for every user in query
    for usr in queryset:
        try:
            if usr.requested_group_name == "":
                if request is not None:
                    messages.error(request, "System error, requested group name blank")
                continue
            #: Check for existing IAM group in resources for cloudformation
            group_exists = os.path.isdir(os.path.join(user_profiles, 'group-' + str(usr.requested_group_name)))
            #: Generate one if there isn't an existing folder
            if not group_exists:
                command = 'source ~/ncap/venv/bin/activate && cd ~/ncap/neurocaas/ncap_iac/user_profiles/iac_utils && bash ' + str(os.path.join(user_profiles, 'iac_utils/configure.sh')) + ' group-' + str(usr.requested_group_name)
                process = subprocess.Popen([command],
                                stdout=None,
                                stderr=None,
                                shell=True,
                                executable='/bin/bash')
                process.communicate()
            user_config_array = {}
            #: Fill correct JSON data for cloudformation
            try:
                with open(os.path.join(user_profiles, 'group-' + str(usr.requested_group_name), 'user_config_template.json')) as f:
                    user_config_array = json.load(f)
                    user_exists = False
                    username = make_username(usr)
                    for aff in user_config_array['UXData']["Affiliates"]:
                        if username in aff["UserNames"]:
                            user_exists = True
                    if user_exists:
                        if request!=None:
                            messages.warning(request, "[IGNORE IF ACCESS CHANGE] Duplicate Username or Email. ")
                    else:
                        affiliate = user_config_array['UXData']["Affiliates"][0]
                        if group_exists:
                            affiliate["UserNames"].append(username)
                            affiliate["ContactEmail"].append(usr.email)
                        else:
                            affiliate["AffiliateName"] = usr.requested_group_name
                            affiliate["ContactEmail"] = [usr.email]
                            affiliate["UserNames"] = [username]
                        user_config_array['UXData']["Affiliates"][0] = affiliate

                with open(os.path.join(user_profiles, 'group-' + str(usr.requested_group_name), 'user_config_template.json'), 'w') as outfile:
                    json.dump(user_config_array, outfile)
            except Exception as e:
                if request is not None:
                    messages.error(request, "Backend error 1: " + str(e))
            #: Call deploy.sh script to deploy these resources
            command = 'source ~/ncap/venv/bin/activate && source activate /home/ubuntu/ncap/neurocaas && cd ~/ncap/neurocaas/ncap_iac/user_profiles/iac_utils && ./deploy.sh ' + os.path.join(user_profiles,'group-' + str(usr.requested_group_name) + ' &')
            outfile = open('logs/iam_creation_out_log.txt','a')
            errfile = open('logs/iam_creation_err_log.txt','a')
            process = subprocess.Popen([command],
                            stdout=outfile, 
                            stderr=errfile,
                            shell=True, 
                            executable='/bin/bash')
            process.communicate()
            if request is not None:
                messages.add_message(request, messages.INFO, 
                "The IAM Creation Process has started. Please check back later to see if your resources have been created.")
        except Exception as e:
            if request is not None:
                messages.error(request, "Backend Error 0: " + str(e))
register_IAM.short_description = "[LEGACY] Generate IAMs for selected users"
#: Removes IAM Automatically with AWS and the Django DB
def remove_IAM(modeladmin, request, queryset):
    #: Remove IAM for every user in query
    for usr in queryset:
        #: Check that the user has an IAM already
        if len(IAM.objects.filter(user=usr)) > 0:   # pragma: no cover
            user_config_array = {}
            current_iam = IAM.objects.filter(user=usr).first()
            current_group = current_iam.group
            #: Remove correct JSON data for cloudformation
            with open(os.path.join(user_profiles, 'group-' + str(current_group), 'user_config_template.json')) as f:
                user_config_array = json.load(f)
                affiliate = user_config_array['UXData']["Affiliates"][0]
                curren_un = current_iam.aws_user.replace(user_config_array['Lambda']['LambdaConfig']['REGION'],'')
                if (curren_un in affiliate["UserNames"]):
                    #: Then IAM exists in the data, and you can Remove the IAM
                    affiliate["UserNames"].remove(curren_un)
                user_config_array['UXData']["Affiliates"][0] = affiliate
            with open(os.path.join(user_profiles, 'group-' + str(current_group), 'user_config_template.json'), 'w') as outfile:
                json.dump(user_config_array, outfile)
            #: Call deploy.sh script to deploy these resources
            command = 'source ~/ncap/venv/bin/activate && cd ~/ncap/neurocaas/ncap_iac/user_profiles/iac_utils && ./deploy.sh ' + os.path.join(user_profiles,'group-' + str(current_group) + ' &')
            outfile = open('logs/iam_removal_out_log.txt','a')
            errfile = open('logs/iam_removal_err_log.txt','a')
            process = subprocess.Popen([command],
                            stdout=outfile,
                            stderr=errfile,
                            shell=True,
                            executable='/bin/bash')
            process.communicate()
            messages.add_message(request, messages.INFO, "The IAM Removal Process has started. Please check back later to see if your resources have been removed.")
            #: Remove IAM from django db
            current_iam.delete()
        else:
            messages.error(request, "A user was selected that did not contain a valid IAM")
remove_IAM.short_description = "[LEGACY] Remove IAMs for selected users [Run before deleting]"

def changeGroupPermissions(modeladmin, request, queryset):  # pragma: no cover
    #: redirects to intermediate page which lets you change the permissions of a specific queryset. 
    #: Then this should call iam_create after updating perms as in analysis_deploy.py
    logfile = open('logs/iam_change_perms_log.txt','w')
    logfile.write("pre apply\n")
    logfile.write(json.dumps(request.POST))
    logfile.write("\nafter post data")
    group_access = []
    if 'apply' in request.POST:
        logfile.write("Hit apply")
        # The user clicked submit on the intermediate form.
        # Perform our update action:
        path = "/home/ubuntu/ncap/neurocaas/ncap_iac/user_profiles"
        for usr in queryset:  
            if len(IAM.objects.filter(user=usr)) == 0:
                messages.error(request, "Select a user with an IAM")
                continue
            stack = "group-" + IAM.objects.filter(user=usr)[0].group.name
            new_path = path + "/" + stack
            if os.path.isdir(new_path):
                try:
                    with open(new_path + "/user_config_template.json") as f:
                        try:
                            data_array = json.load(f)
                            #pipelines = data_array['UXData']["Affiliates"][0]["Pipelines"]
                            pipelines = []
                            for ana in Analysis.objects.all():
                                if(ana.bucket_name in request.POST):
                                    pipelines.append(ana.bucket_name)
                                    group_access.append(ana)
                            data_array['UXData']["Affiliates"][0]["Pipelines"] = pipelines
                            with open(new_path + "/user_config_template.json", 'w') as outfile:
                                json.dump(data_array, outfile)
                            logfile.write("Succeeded on stack: " + stack)
                        except:
                            logfile.write("Failed on stack: " + stack)
                except:
                    logfile.write("ignored folder: " + new_path)
        # Redirect to our admin view after our update has 
        # completed with a  message  
        messages.add_message(request, messages.INFO, "Attempting permission redeployment...")
        register_IAM(modeladmin, request, queryset)
        for usr in queryset:
            for ana in Analysis.objects.all():
                if ana in group_access:
                    if not IAM.objects.filter(user=usr)[0].group in ana.groups.all():
                        ana.groups.add(IAM.objects.filter(user=usr)[0].group)
                else:
                    if IAM.objects.filter(user=usr)[0].group in ana.groups.all():
                        ana.groups.remove(IAM.objects.filter(user=usr)[0].group)

        return HttpResponseRedirect(request.get_full_path())
    return render(request,
                      'admin/change_ana_access.html',
                      context={'analyses':Analysis.objects.all(), 'changeiams':queryset})
    
changeGroupPermissions.short_description = "[LEGACY] Update Group Perms"

class UserAdministrator(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm

    list_display = ('email', 'is_admin', 'last_name', 'requested_group_code','group')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'has_migrated_pwd', 'first_name', 'last_name', 'use_code', 'requested_group_code','group','cred_expire')}),
        ('Permissions', {'fields': ('data_transfer_permission',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'has_migrated_pwd', 'first_name', 'last_name', 'data_transfer_permission','use_code','requested_group_name','requested_group_code','group')}
         ),
    )
    actions = [register_IAM, remove_IAM, changeGroupPermissions]
    def IAM_attached(self, obj):
        if len(IAM.objects.filter(user=obj)) == 1:
            return True
        return False
    IAM_attached.boolean = True

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

@admin.register(IAM)
class IAMAdmin(admin.ModelAdmin):
    list_display = ('user', 'aws_user', 'aws_access_key', 'group', 'created_on')
    readonly_fields = ['group']
    search_fields = ('user',)
    ordering = ('aws_user',)

@admin.register(AnaGroup)
class AWSAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_on')
    readonly_fields=('code',)

admin.site.register(User, UserAdministrator)
admin.site.unregister(Group)