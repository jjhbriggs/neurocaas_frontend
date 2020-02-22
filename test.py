import boto3
from datetime import datetime

s3 = boto3.resource(
    's3',
    aws_access_key_id="AKIA2YSWAZCCRK2H3SHJ",
    aws_secret_access_key="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")

obj = s3.Object("epi-ncap", "cunninghamlabEPI/results/jobepi_demo/hp_optimum/epi_opt1.mp4")
body = obj.get()
# print(body['ResponseMetadata']['HTTPHeaders']['last-modified'])

format_date = datetime.strptime(body['ResponseMetadata']['HTTPHeaders']['last-modified'], '%a, %d %b %Y %H:%M:%S GMT')
print(format_date.timestamp())
