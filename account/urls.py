from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('instruction/', TemplateView.as_view(template_name="account/instruction.html"), name='instruction'),
    path('iamcreate/', IamCreateView.as_view(), name='iam_create_view'),
    path('changepwd/', ChangePWD2.as_view(), name='change_password'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="account/reset_password.html", subject_template_name="account/password_reset_subject.txt", email_template_name="account/password_reset_email.html"), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="account/reset_password_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="account/reset_password_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="account/reset_password_complete.html"), name='password_reset_complete'),
    
]
