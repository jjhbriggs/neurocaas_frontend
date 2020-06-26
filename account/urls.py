from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('aws_cred_request/', AWSCredRequestView.as_view(), name='aws_cred_request'),
    path('instruction/', TemplateView.as_view(template_name="account/instruction.html"), name='instruction'),
    path('iamcreate/', IamCreateView.as_view(), name='iam_create_view'),
    path('changepwd/', ChangePWD2.as_view(), name='change_password'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='account/login.html')),
]

'''path('login2/', LoginView2.as_view(), name='login2'),
    path('register2/', RegisterView2.as_view(), name='register2'),'''
    
'''kwargs={'iam': IAM.objects.filter(user=request.user).first() if request.user.is_authenticated else None,
            'user': request.user if not request.user.is_anonymous else None,
            'logged_in': not request.user.is_anonymous}),
            
            
            
            path('changepwd/', PasswordChangeView.as_view(template_name='account/change_password.html',
            success_url = '/changepwd/'), name='password_change'),'''