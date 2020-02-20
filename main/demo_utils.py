import boto3
from .models import *
import os


def get_matching_s3_objects(bucket,
                            aws_access_key_id,
                            aws_secret_access_key,
                            prefix='',
                            suffix='',
                            max_keys_per_request=1,
                            startafter=""):
    """
    List objects in an S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    :param max_keys_per_request: number of objects to list down
    """
    s3 = boto3.client('s3',
                      aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)
    kwargs = {'Bucket': bucket}

    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix
    else:
        kwargs['Prefix'] = str(prefix)

    if startafter:
        kwargs['StartAfter'] = startafter

    kwargs['MaxKeys'] = max_keys_per_request

    while True:
        resp = s3.list_objects_v2(**kwargs)

        try:
            contents = resp['Contents']
        except KeyError:
            return

        for obj in contents:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield obj

        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def get_matching_s3_keys(bucket,
                         aws_access_key_id,
                         aws_secret_access_key,
                         prefix='',
                         suffix='',
                         max_keys_per_request=1,
                         startafter=""):
    """
    Generate the keys in an S3 bucket.
    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    :param max_keys_per_request: number of objects to list down
    """
    for obj in get_matching_s3_objects(bucket=bucket,
                                       aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key,
                                       prefix=prefix,
                                       suffix=suffix,
                                       max_keys_per_request=max_keys_per_request,
                                       startafter=startafter):
        yield obj['Key']


def get_list_of_tables(root_path_or_bucket,
                       extract_path,
                       aws_access_key_id=None,
                       aws_secret_access_key=None,
                       file_extension=".mp4",
                       startafter=""):
    """
    Method to list down the tables under given snapshot path prefixed as:
    bucket_name/cunninghamlabEPI/results/{tables}
    :param root_path_or_bucket:
    :param extract_path: Path that leads to all tables organised date wise
    :return: tables : Array of keys
    """
    tables = []

    if len(extract_path) > 0:
        print(
            "Listing the s3 bucket {}/{}! Will take a little while...".format(root_path_or_bucket, extract_path))
        for key in get_matching_s3_keys(bucket=root_path_or_bucket,
                                        aws_access_key_id=aws_access_key_id,
                                        aws_secret_access_key=aws_secret_access_key,
                                        prefix=extract_path,
                                        suffix=file_extension,
                                        max_keys_per_request=1000,
                                        startafter=startafter):
            splited_path = key.split("/")
            subfolder = splited_path[2]
            tables.append(subfolder)

    return list(set(tables))


def get_download_file(iam, bucket, key, proc_name):
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
        print(e)
        return None


#####################################################
def check_process(iam, process):
    BASE = 'cunninghamlabEPI/results'
    root_path_or_bucket = process.uploaded_file.bucket.name
    last_proc = Process.objects.all().order_by('-created_on')[1]

    if process.local_file:
        return process.local_file

    elif process.s3_path:
        result_key = "%s/%s/search_output/epi_opt.mp4" % (BASE, last_proc.s3_path)
        file_path = get_download_file(iam=iam, bucket=root_path_or_bucket, key=result_key, proc_name=process.name)
        if file_path:
            process.local_file = file_path
            process.save()
            return file_path
        else:
            return None

    extract_path = "cunninghamlabEPI/results"
    file_extension = ".mp4"
    startafter = "%s/%s/" % (BASE, last_proc.s3_path)

    folder_lists = get_list_of_tables(root_path_or_bucket=root_path_or_bucket,
                                      extract_path=extract_path,
                                      aws_access_key_id=iam.aws_access_key,
                                      aws_secret_access_key=iam.aws_secret_access_key,
                                      file_extension=file_extension,
                                      startafter=startafter)
    if len(folder_lists) > 1:
        process.s3_path = folder_lists[1]
        process.save()

    return None
