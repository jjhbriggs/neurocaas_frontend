from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from account.models import IAM, User


def authenticate( email=None, password=None):
    '''try:
        customer = User.objects.filter(email=email,
                                      password=password).first()
        if customer:
            return customer
    except User.DoesNotExist:
        pass'''
    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            return user
    except User.DoesNotExist:
            return None
