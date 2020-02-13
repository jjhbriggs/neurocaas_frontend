from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from account.models import IAM, User


def authenticate( aws_access_key=None, aws_secret_access_key=None):
    try:
        customer = IAM.objects.filter(aws_access_key=aws_access_key,
                                      aws_secret_access_key=aws_secret_access_key).first()
        if customer:
            return customer.user
    except User.DoesNotExist:
        pass
