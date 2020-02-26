from django.urls import path, include
from .views import *


urlpatterns = [
    path('', HomeView.as_view(template_name="main/home.html"), name="home"),

    #""" demo """
    path('demo/', DemoView.as_view(), name='demo'),
    path('demo_result/', DemoResultView.as_view(), name='demo_result'),
]
