from django.urls import path, include
from .views import *


urlpatterns = [
    path('', HomeView.as_view(template_name="main/home.html"), name="home"),

    #""" demo """
    path('demo/', DemoView.as_view(), name='demo'),
    path('demo_result/', DemoResultView.as_view(), name='demo_result'),
    path('demo_bucket/', DemoDataBucketView.as_view(), name='data_bucket'),

    # demo 2
    path('demo2/', MainView.as_view(), name='demo2'),
    path('get_user_files/', UserFilesView.as_view(), name='get_user_files'),
    path('get_results/', ResultView.as_view(), name='get_results')
]
