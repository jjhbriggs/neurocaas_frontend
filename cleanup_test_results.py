import boto3
import os


s3 = boto3.resource('s3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
bucket = s3.Bucket("cianalysispermastack")

with open("prefixes_for_delete.txt", "r+") as f:
    content = f.readlines()
    content = [x.strip() for x in content]
    num = 0
    for pref in content:
        num += 1
        for obj in bucket.objects.filter(Prefix=pref):
	        obj.delete()
        print("Deleted " + pref)
    if num == 0:
        print("Nothing to remove")
    f.truncate(0)
