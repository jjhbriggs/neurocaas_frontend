from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView


urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('aws_cred_request/', AWSCredRequestView.as_view(), name='aws_cred_request'),
    path('instruction/', TemplateView.as_view(template_name="account/instruction.html"), name='instruction'),
    path('iamcreate/', IamCreateView.as_view(), name='iam_create_view'),
]

