import sys
import os
import csv
import json
import logging
from django.core.management.base import BaseCommand
from account.models import *
from main.models import Analysis
from django.core.mail import send_mail
#: This script is a custom django management command
#: This should be called in the ~/ncap folder with python manage.py register_creds [PIPEDIR]
class Command(BaseCommand):
    help = 'Registers IAMs and Ana_groups with the django database'

    def add_arguments(self, parser):
        parser.add_argument('pipe_dir', nargs='+', type=str)

    def handle(self, *args, **options):
        logging.basicConfig(filename="email_log.txt",
                            filemode='a',
                            format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
                            datefmt="%Y-%m-%d %H:%M:%S",
                            level=logging.DEBUG)
        pipedir = options.get('pipe_dir', None)[0]
        pipename = os.path.basename(pipedir)
        #: Get Data from user_config_template
        with open(os.path.join(pipedir, 'user_config_template.json')) as f:
            user_config_array = json.load(f)
            affiliate_num = 0
            for affiliate in user_config_array['UXData']["Affiliates"]:
                ana_name = affiliate["AffiliateName"]
                usernames = affiliate["UserNames"]
                pipelines = affiliate["Pipelines"]
                region = user_config_array["Lambda"]["LambdaConfig"]["REGION"]
                #email = affiliate["ContactEmail"][0]
                #: Exit program if these variables aren't set
                if (not 'ana_name' in locals()) or (not 'pipelines' in locals()) or (not 'region' in locals()) or (not 'usernames' in locals()):
                    logging.critical("Fatal Error: couldn't get proper data from user_config_template.json")
                    sys.exit()
                logging.info('Found data in user_config_template')
                #: Make new iam and ana group
                full_path = os.path.join("/home/ubuntu/ncap/ncap_user_creds", pipename)
                directory = os.fsencode(full_path)
                num_new_users = 0
                #: Find all users to create in pipedir
                for username in usernames:
                    with open(os.path.join(full_path, "NCAP_KEY_AUTO_" + username + ".csv"), 'r') as data: 
                        for creds in csv.DictReader(data): 
                            #: IAM and ana_group creation
                            email = affiliate["ContactEmail"][num_new_users]
                            logging.info('Starting iam and ana_group creation for user' + creds['Username'] + region)
                            user = User.objects.filter(email=email).first()
                            new_group = AnaGroup.objects.filter(name=ana_name)
                            if len(new_group) == 0:
                                new_group = AnaGroup.objects.create(name=ana_name)
                            else:
                                new_group = new_group.first()

                            iam_pwd = ""
                            with open(os.path.join(pipedir, 'compiled_users.json')) as f2:
                                user_pwd_array = json.load(f2)
                                iam_pwd = user_pwd_array['Outputs']['Password' + username]['Value']
                                #------user_config_array['Outputs']['Passwordtestmultiplegmail']['Value']
                            if len(IAM.objects.filter(user=user)) == 0:
                                iam = IAM.objects.create(user=user,
                                                    aws_user=creds['Username'] + region,
                                                    aws_access_key=creds['Access Key'],
                                                    aws_secret_access_key=creds['Secret Access Key'],
                                                    aws_pwd = iam_pwd,
                                                    group=new_group)
                            #: Register group with listed buckets
                            for bucket in pipelines:
                                analysis_to_add = Analysis.objects.filter(bucket_name=bucket).first()
                                analysis_to_add.groups.add(new_group)
                            logging.info('Finished iam and ana_group creation for user' + creds['Username'] + region)
                            try:
                                body_string = "Dear " + user.get_full_name() + ",\n\nYour NeuroCAAS Registration was successful, and you have been granted access to begin running analyses.\n\nRegards,\nThe NeuroCAAS Team"
                                send_mail(
                                    'NeuroCAAS Registration Complete',
                                    body_string,
                                    'neurocaas@gmail.com',
                                    [user.email],
                                    fail_silently=False,
                                )
                            except Exception as e:
                                logging.warning("SMTP Client failed:\n" + str(e))
                            num_new_users += 1
                if num_new_users == 0:
                    logging.warning('No user credentials found in ' + full_path + ' matching usernames in user_config_template')
                else:
                    logging.info("-----------------------------------")
                    logging.info(str(num_new_users) + " new users created.")
                affiliate_num = affiliate_num + 1
            if affiliate_num == 0:
                logging.warning('No affiliates found')
            else:
                logging.info("-----------------------------------")
                logging.info(str(affiliate_num) + " affiliates were registered")