import boto3
from datetime import datetime

s3 = boto3.resource(
    's3',
    aws_access_key_id="AKIA2YSWAZCCRK2H3SHJ",
    aws_secret_access_key="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")

"""
    Get Object's last modified data
"""
# obj = s3.Object("epi-ncap", "cunninghamlabEPI/results/jobepi_demo/hp_optimum/epi_opt1.mp4")
# body = obj.get()
# # print(body['ResponseMetadata']['HTTPHeaders']['last-modified'])
#
# format_date = datetime.strptime(body['ResponseMetadata']['HTTPHeaders']['last-modified'], '%a, %d %b %Y %H:%M:%S GMT')
# print(format_date.timestamp())


"""
    Get list of files in s3 bucket sub folder
"""


## Bucket to use
bucket = s3.Bucket("epi-ncap")

## List objects within a given prefix
for obj in bucket.objects.filter(Delimiter='/', Prefix='cunninghamlabEPI/results/jobepi_demo/logs/'):
    print(obj.key)