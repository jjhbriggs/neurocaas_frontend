import json
import os
import sys
import shutil
import time
import boto3
import datetime
import urllib.parse
import requests

from account.models import *
from .models import Analysis
from .sts_utils import *
from datetime import timedelta 
import pytz

def get_current_iam(request):
    """
        Return current iam object from request.
        """
    return IAM.objects.filter(user=request.user).first() if request.user.is_authenticated else None
    

def get_current_user(request):
    """
        Return current user object from request.
        """
    return request.user if not request.user.is_anonymous else None
def s3_resource(iam):
    if iam.fixed_creds:
        return boto3.resource(
            's3',
            aws_access_key_id=iam.aws_access_key,
            aws_secret_access_key=iam.aws_secret_access_key)
    return boto3.resource(
            's3',
            aws_access_key_id=iam.aws_access_key,
            aws_secret_access_key=iam.aws_secret_access_key,
            aws_session_token=iam.aws_session_token)

def get_current_analysis(ana_id):
    """
        Get current analysis from analysis id stored in session.
        """
    analysis = Analysis.objects.get(pk=ana_id)
    return analysis


def mkdir(path):
    """
        Create new folder by path.
        """
    if not os.path.exists(path):
        os.makedirs(path)


def convert_size(size):
    """
        Return size converted to appropriate format from Byte.
        """
    if size > 1024 * 1024 * 1024:
        return str(round(float(size / (1024 * 1024 * 1024)), 2)) + " GB"
    elif size > 1024 * 1024:
        return str(round(float(size / (1024 * 1024)), 2)) + " MB"
    elif size > 1024:
        return str(round(float(size / 1024), 2)) + " KB"
    else:
        return str(size) + " B"


def get_name_only(key):
    """
        Function to get only file name from link or full path.
        """
    return key.split('/')[-1]


def get_list_keys(iam, bucket, folder, un_cert=True):
    """
        Return keys of files and folders in s3.

        @params:
                iam: User's IAM object
                bucket: bucket name
                folder: folder path on s3 bucket

        @return:
                list of files and folders
        """
    s3 = s3_resource(iam=iam)

    bucket = s3.Bucket(bucket)
    prefix = "%s/" % folder

    file_keys = []

    # try:
    for obj in bucket.objects.filter(Prefix=prefix):
        if un_cert and obj.key.endswith('certificate.txt'):
            continue
        if obj.key.count('internal_ec2_logs') or obj.key == prefix or \
                obj.key.endswith('end.txt') or obj.key.endswith('update.txt'):
            continue
        file_keys.append(obj.key)
    # except Exception as e:
    #     print(e)

    return file_keys


def generate_folder():
    """Generate folder with current time."""
    return "%s/%s" % ("static/downloads", time.time())


def upload_file_to_s3(iam, bucket, key, file_path):
    """
        Download file from s3 and return link of it.
        """
    s3 = s3_resource(iam=iam)
    
    return s3.Bucket(bucket).upload_file(file_path,key)
def download_file_from_s3(iam, bucket, key, folder):
    """
        Download file from s3 and return link of it.
        """
    s3 = s3_resource(iam=iam)

    mkdir(folder)
    file_path = "%s/%s" % (folder, get_name_only(key))
    try:
        s3.Bucket(bucket).download_file(key, file_path)
    except Exception as e:
        print(e)
        return None

    return file_path

def download_directory_from_s3(iam, bucket, folder, un_cert=True):
    """
        Download a folder from s3 bucket,

        @params:
                iam: User IAM Object
                bucket: bucket name
                folder: folder on s3 bucket
                un_cert: flag for certificate.txt file, if True, result will not contain cert.txt, if not, it contains.
        @return:
                downloaded directory location
        """

    s3 = s3_resource(iam=iam)

    timestamp = time.time()
    # create folders
    root = "static/downloads/%s" % timestamp
    mkdir("static/downloads")
    mkdir(root)

    keys = get_list_keys(iam=iam, bucket=bucket, folder=folder, un_cert=un_cert)
    bucket = s3.Bucket(bucket)
    for key in keys:
        path = "%s/%s" % (root, key.replace(folder, ''))
        mkdir(os.path.dirname(path))
        if key.endswith('/'):
            continue

        bucket.download_file(key, path)

    return root


def get_last_modified_timestamp(iam, bucket, key):
    """
        Return file's timestamp on s3 bucket.

        @params:
                iam: User's IAM object
                bucket: bucket name
                key: file key on s3 bucket

        @return:
                timestamp of file
        """
    s3 = s3_resource(iam=iam)
    obj = s3.Object(bucket, key)
    try:
        body = obj.get()
        _date = datetime.datetime.strptime(body['ResponseMetadata']['HTTPHeaders']['last-modified'], '%a, %d %b %Y %H:%M:%S GMT')
        return _date.timestamp()
    except Exception as e:
        print(e)

    return 0


def get_file_content(iam, bucket, key):
    """
        Return content of file in s3.

        @params:
                iam: User's IAM object
                bucket: bucket name
                key: file key on s3 bucket

        @return:
                content of file
        """
    s3 = s3_resource(iam=iam)
    obj = s3.Object(bucket, key)

    try:
        body = obj.get()['Body'].read().decode('utf-8')
        return body
    except Exception as e:
        print(e)
        return None


def get_data_set_logs(iam, bucket, timestamp):
    """
        Retrieve logs' keys for each data set.

        @params:
                iam: User IAM Object
                bucket: bucket name
                timestamp: id of job (timestamp)
        @return:
                key list of data set log
        """

    data_set_logs = []
    log_dir = "%s/results/job__%s_%s/logs/" % (iam.group.name, bucket, timestamp)
    file_keys = get_list_keys(iam=iam, bucket=bucket, folder=log_dir)

    for key in file_keys:
        path = key.replace("%s/results/job__%s_%s/" % (iam.group.name, bucket, timestamp), "")
        data_set_logs.append({
            'path': path
        })

    return data_set_logs


def get_job_list(iam, bucket, folder):
    """
        Retrieve job list from s3.

        @params:
                iam: User IAM Object
                bucket: bucket name
                folder: folder in s3
        @return:
                folder list of jobs
        """
    if iam.fixed_creds:
        s3 = boto3.client('s3',
                      aws_access_key_id=iam.aws_access_key,
                      aws_secret_access_key=iam.aws_secret_access_key)
    else:
        s3 = boto3.client('s3',
                      aws_access_key_id=iam.aws_access_key,
                      aws_secret_access_key=iam.aws_secret_access_key,
                      aws_session_token=iam.aws_session_token)
    prefix = "%s/" % folder
    job_key_list = []
    try:
        all_objects = s3.list_objects(Bucket=bucket, Delimiter='/', Prefix=prefix)
        for obj in all_objects['CommonPrefixes']:
            if obj['Prefix'].endswith(prefix):
                continue
            key = obj['Prefix'][:-1].replace(prefix, '')
            job_key_list.append({
                'name': key,
                'timestamp': key.split('_')[-1]
            })

    except Exception as e:
        print(e)

    return job_key_list


# function to get all files only of folder in bucket
def get_files_detail_list(iam, bucket, folder):
    """
        Retrieve file list and its detail content from s3.

        @params:
                iam: User IAM Object
                bucket: bucket name
                folder: folder in s3
        @return:
                list of files with its detail (last_modified and size)
        """
    s3 = s3_resource(iam=iam)

    bucket = s3.Bucket(bucket)

    file_details = []

    prefix = "%s/" % folder

    # Retrieve keys from s3 bucket
    try:
        objects = bucket.objects.filter(Prefix=prefix)
        for obj in objects:
            if obj.key.count('internal_ec2_logs') or obj.key == prefix or obj.key.endswith('/'):
                continue
            file_details.append({
                'key': obj.key,
                'date_modified': obj.last_modified.strftime('%Y-%m-%d'),
                'size': convert_size(obj.size)
            })
    except Exception as e:
        print(e)

    return file_details


def delete_folder_from_bucket(iam, bucket, prefix):
    """
        Delete a folder from s3 bucket.

        @params:
                iam: User IAM Object
                bucket: bucket name
                prefix: prefix for filter (folder name)
        @return:
                delete folder from s3
        """
    s3 = s3_resource(iam=iam)
    bucket = s3.Bucket(bucket)
    for obj in bucket.objects.filter(Prefix=prefix):
        obj.delete()


def delete_file_from_bucket(iam, bucket, key):
    """
        Delete a file from s3 bucket.

        @params:
                iam: User IAM Object
                bucket: bucket name
                key: file key
        @return:
                delete a file from s3
        """
    s3 = s3_resource(iam=iam)
    obj = s3.Object(bucket, key)
    obj.delete()


def create_submit_json(iam, bucket, key, json_data):
    """
        Create submit.json object with json data.

        @params:
                iam: User IAM Object
                bucket: bucket name
                key: json file key
                json_data: json data
        @return:
                None
        """
    s3 = s3_resource(iam=iam)
    s3object = s3.Object(bucket, key)

    s3object.put(
        Body=(bytes(json.dumps(json_data).encode('UTF-8')))
    )
    print("successfully created submit.json")

def groupname_from_user(user):
    return (user.email.replace('@', '').replace('.', '').replace('_', '-')[0:12] + str((user.time_added.hour * 60 + user.time_added.minute) * 60 + user.time_added.second))
def build_credentials(group, analysis,testing=False):
    #: Returns object with temporary credentials

    iam_res = boto3.resource('iam',aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    name_function = unique_testing_name if testing else unique_name
    role = setup(iam_res,name_function)
    sts_client = boto3.client('sts',aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
    return generate_credentials(role.arn, 'AssumeRoleDemoSession', sts_client, group.name, analysis.bucket_name) 

def reassign_iam(iam, temp_credentials):
    iam.aws_access_key = temp_credentials['AccessKeyId']
    iam.aws_secret_access_key = temp_credentials['SecretAccessKey']
    iam.aws_session_token = temp_credentials['SessionToken']
    iam.save()

def construct_federated_url(iam, issuer, bucket):
    """
    Constructs a URL that gives federated users direct access to the AWS Management
    Console.
       Builds a URL that can be used in a browser to navigate to the AWS federation
       endpoint, includes the sign-in token for authentication, and redirects to
       the AWS Management Console with permissions defined by the role that was
       specified in step 1.

    :param issuer: The organization that issues the URL.
    :return: The federated URL.
    """

    session_data = {
        'sessionId': iam.aws_access_key,
        'sessionKey': iam.aws_secret_access_key,
        'sessionToken': iam.aws_session_token
    }
    aws_federated_signin_endpoint = 'https://signin.aws.amazon.com/federation'

    # Make a request to the AWS federation endpoint to get a sign-in token.
    # The requests.get function URL-encodes the parameters and builds the query string
    # before making the request.
    response = requests.get(
        aws_federated_signin_endpoint,
        params={
            'Action': 'getSigninToken',
            'SessionDuration': str(datetime.timedelta(hours=12).seconds),
            'Session': json.dumps(session_data)
        })
    signin_token = json.loads(response.text)
    print(f"Got a sign-in token from the AWS sign-in federation endpoint.")

    # Make a federated URL that can be used to sign into the AWS Management Console.
    query_string = urllib.parse.urlencode({
        'Action': 'login',
        'Issuer': issuer,
        'Destination': 'https://s3.console.aws.amazon.com/s3/buckets/'+bucket+'?region=us-east-1&prefix='+iam.group.name+'/inputs/&showversions=false',
        'SigninToken': signin_token['SigninToken']
    })
    federated_url = f'{aws_federated_signin_endpoint}?{query_string}'
    return federated_url
def _deletion_filter(role):
    return role.role_name.startswith("sts-role-") and pytz.utc.localize(datetime.datetime.now()) > (role.create_date+timedelta(seconds=role.max_session_duration)).astimezone(pytz.utc)
def _deletion_filter_testing(role):
    return role.role_name.startswith("sts-testing-role-")
def sts_teardown_all(testing=False):
    for role in filter(_deletion_filter_testing if testing else _deletion_filter,boto3.resource('iam',aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')).roles.all()):
        teardown(role)