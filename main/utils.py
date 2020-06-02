import json
import os
import shutil
import time
import boto3

from account.models import *
from .models import Analysis


def get_current_iam(request):
    """
        return current iam object from request
        """
    return IAM.objects.filter(user=request.user).first() if request.user.is_authenticated else None


def get_current_analysis(request):
    """
        get current analysis from analysis id stored in session
        """
    ana_id = request.session.get('ana_id', 1)
    analysis = Analysis.objects.get(pk=ana_id)
    return analysis


def mkdir(path):
    """
        create new folder by path
        """
    if not os.path.exists(path):
        os.makedirs(path)


def get_download_file(iam, bucket, key, timestamp):
    """
        Download file from s3 and return link of it
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key
    )
    parent_folder = "static/downloads"
    mkdir(parent_folder)
    folder = "static/downloads/%s" % timestamp
    mkdir(folder)

    output = "%s/%s" % (folder, key.split("/")[-1])
    try:
        s3.Bucket(bucket).download_file(key, output)
    except Exception as e:
        print(e)
        return None

    return output


def get_last_modified_timestamp(iam, bucket, key):
    """
        Return last process files' timestamp
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key
    )
    obj = s3.Object(bucket, key)
    try:
        body = obj.get()
        _date = datetime.strptime(body['ResponseMetadata']['HTTPHeaders']['last-modified'], '%a, %d %b %Y %H:%M:%S GMT')
        return _date.timestamp()
    except Exception as e:
        print(e)

    return 0


def get_file_content(iam, bucket, key):
    """
        Get content of file by key in s3
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key
    )
    obj = s3.Object(bucket, key)

    try:
        body = obj.get()['Body'].read().decode('utf-8')
        return body
    except Exception as e:
        print(e)
        return None


def get_data_set_logs(iam, bucket, log_dir):
    """
        Retrieve logs for each dataset
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key
    )

    # Bucket to use
    bucket = s3.Bucket(bucket)

    # log files
    file_keys = []
    # List objects within a given prefix
    try:
        for obj in bucket.objects.filter(Delimiter='/', Prefix=log_dir):
            if obj.key.endswith('certificate.txt'):
                continue
            file_keys.append(obj.key)
    except Exception as e:
        print(e)

    return file_keys


def convert_size(size):
    """
        Return size converted to appropriate format from Byte
    """
    if size > 1024 * 1024 * 1024:
        return str(round(float(size / (1024 * 1024 * 1024)), 2)) + " GB"
    elif size > 1024 * 1024:
        return str(round(float(size / (1024 * 1024)), 2)) + " MB"
    elif size > 1024:
        return str(round(float(size / 1024), 2)) + " KB"
    else:
        return str(size) + " B"


def get_job_list(iam, bucket, folder):
    """
       return only job folder list
        """
    s3 = boto3.client('s3',
                      aws_access_key_id=iam.aws_access_key,
                      aws_secret_access_key=iam.aws_secret_access_key)
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
def get_file_list(iam, bucket, folder):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)

    bucket = s3.Bucket(bucket)

    file_keys = []

    prefix = "%s/" % folder

    # Retrieve keys from s3 bucket
    try:
        objects = bucket.objects.filter(Prefix=prefix)
        for obj in objects:
            if obj.key.count('internal_ec2_logs') or obj.key == prefix or obj.key.endswith('/'):
                continue
            file_keys.append({
                'key': obj.key,
                'date_modified': obj.last_modified.strftime('%Y-%m-%d'),
                'size': convert_size(obj.size)
            })

    except Exception as e:
        print(e)

    return file_keys


def get_list_keys(iam, bucket, folder):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)

    bucket = s3.Bucket(bucket)
    prefix = "%s/" % folder

    file_keys = []

    for obj in bucket.objects.filter(Prefix=prefix):
        if obj.key.count('internal_ec2_logs') or obj.key == prefix or obj.key.endswith('end.txt') or obj.key.endswith('update.txt'):
            continue
        file_keys.append(obj.key)

    return file_keys


def get_name_only(key):
    """
        Function to get only file name from link or full path
        """
    return key.split('/')[-1]


def delete_folder_from_bucket(iam, bucket_name, prefix):
    """
        Delete existing json files from s3 before start new job
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Delimiter='/', Prefix=prefix):
        obj.delete()


def delete_file_from_bucket(iam, bucket_name, key):
    """
        Delete a file from s3 bucket
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)
    obj = s3.Object(bucket_name, key)
    obj.delete()


def create_submit_json(iam, work_bucket, key, json_data):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)
    s3object = s3.Object(work_bucket, key)

    s3object.put(
        Body=(bytes(json.dumps(json_data).encode('UTF-8')))
    )
    print("successfully created submit.json")


def download_directory_from_s3(iam, bucket, folder):
    s3_resource = boto3.resource('s3',
                                 aws_access_key_id=iam.aws_access_key,
                                 aws_secret_access_key=iam.aws_secret_access_key)
    bucket = s3_resource.Bucket(bucket)
    timestamp = time.time()
    root = "static/downloads/%s" % timestamp
    mkdir(root)

    for obj in bucket.objects.filter(Prefix=folder):
        if obj.key.count('internal_ec2_logs') or obj.key.endswith('certificate.txt') or \
                obj.key.endswith('end.txt') or obj.key.endswith('update.txt'):
            continue
        path = "%s/%s" % (root, obj.key.replace(folder, ''))
        mkdir(os.path.dirname(path))
        if obj.key.endswith('/'):
            continue
        bucket.download_file(obj.key, path)
    return root
