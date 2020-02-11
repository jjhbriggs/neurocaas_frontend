from django.urls import path, include
from .views import *
from django.contrib.auth import views as auth_views
from account.forms import UserLoginForm


urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name="account/login.html", authentication_form=UserLoginForm),
         name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
]
