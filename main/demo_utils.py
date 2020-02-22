import boto3
from .models import *
import os
import os, shutil


search_outputdir = "hp_optimum"


def get_download_file(iam, bucket, key, proc_name):
    """
        Download file from s3 and return link of it
        """
    try:
        s3 = boto3.resource(
            's3',
            aws_access_key_id=iam.aws_access_key,
            aws_secret_access_key=iam.aws_secret_access_key
        )

        folder = "static/downloads/%s" % proc_name
        if not os.path.exists(folder):
            os.mkdir(folder)

        output = "%s/epi_opt.mp4" % folder
        s3.Bucket(bucket).download_file(key, output)

        return output
    except Exception as e:
        print(key)
        print(e)
        return None


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
        body = obj.get()['Content']
        return body
    except:
        return None