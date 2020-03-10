import json
import os
import shutil

import boto3

from .models import *

search_outputdir = "hp_optimum"


def get_download_file(iam, bucket, key):
    """
        Download file from s3 and return link of it
        """
    # try:
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key
    )

    folder = "static/downloads"
    if not os.path.exists(folder):
        os.mkdir(folder)

    output = "%s/%s" % (folder, key.split("/")[-1])
    print(key)
    s3.Bucket(bucket).download_file(key, output)

    return output
    # except Exception as e:
    #     print(key)
    #     print(e)
    #     return None


def get_last_modified_timestamp(iam, bucket, key):
    """
        Return last process files' timestamp
    """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key
    )

    # obj = s3.Object("epi-ncap", "cunninghamlabEPI/results/jobepi_demo/hp_optimum/epi_opt.mp4")
    obj = s3.Object(bucket, key)

    try:
        body = obj.get()
        # print(body['ResponseMetadata']['HTTPHeaders']['last-modified'])
        _date = datetime.strptime(body['ResponseMetadata']['HTTPHeaders']['last-modified'], '%a, %d %b %Y %H:%M:%S GMT')
        return _date.timestamp()
    except Exception as e:
        print(e)

    return 0


def remove_files():
    """
        Remove last process files on server
        """
    folder = 'static/downloads'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def get_file_content(iam, bucket, key):
    """
        Get content of file by key in s3
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key
    )

    # obj = s3.Object("epi-ncap", "cunninghamlabEPI/results/jobepi_demo/hp_optimum/epi_opt.mp4")
    obj = s3.Object(bucket, key)

    try:
        body = obj.get()['Body'].read().decode('utf-8')
        return body
    except Exception as e:
        print(e)
        return None


def get_dataset_logs(iam, bucket):
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
    for obj in bucket.objects.filter(Delimiter='/', Prefix='cunninghamlabEPI/results/jobepi_demo/logs/'):
        if obj.key.endswith('certificate.txt'):
            continue
        file_keys.append(obj.key)

    return file_keys


# function to get all files of folder in bucket
def get_file_list(iam, folder):
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)

    bucket = s3.Bucket(iam.data_bucket.name)

    file_keys = []

    prefix = "%s/" % folder

    # Retrieve keys from s3 bucket
    # try:
    for obj in bucket.objects.filter(Delimiter='/', Prefix=prefix):
        if obj.key.endswith('.json'):
            file_keys.append(obj.key)
    # except Exception as e:
    #     print(e)
    return file_keys


def get_name_only(key):
    """
        Function to get only file name from link or full path
        """
    return key.split('/')[-1]


def copy_file_to_bucket(iam, from_bucket, from_key, to_bucket, to_key):
    """
        Copy file from data bucket and paste to work bucket
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)
    copy_source = {
        'Bucket': from_bucket,
        'Key': from_key
    }
    bucket = s3.Bucket(to_bucket)
    bucket.copy(copy_source, to_key)


def delete_jsons_from_bucket(iam, bucket_name, prefix):
    """
        Delete existing json files from s3 before start new job
        """
    s3 = boto3.resource(
        's3',
        aws_access_key_id=iam.aws_access_key,
        aws_secret_access_key=iam.aws_secret_access_key)
    bucket = s3.Bucket(bucket_name)

    for obj in bucket.objects.filter(Delimiter='/', Prefix=prefix):
        if obj.key.endswith('.json'):
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