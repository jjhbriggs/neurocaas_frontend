import boto3
import os


s3 = boto3.resource('s3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
bucket = s3.Bucket("cianalysispermastack")
        
object = s3.Object('cianalysispermastack', 'frontendtravisci/results/prefixes_for_delete.txt')
content = object.get()['Body'].read().decode('utf-8') 

content = content.split('\n')
del content[-1]

num = 0
for pref in content:
    for obj in bucket.objects.filter(Prefix=pref):
        num += 1
        obj.delete()
        print("Object found:" + str(obj))
    print("Deleted " + pref)
if num == 0:
    print("Nothing to remove")
object.put(Body="")
