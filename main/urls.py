from django.urls import path, include
from .views import *
from django.views.generic import TemplateView


urlpatterns = [
    path('', TemplateView.as_view(template_name="main/home.html"), name="home"),

    path('step1/', SelectBucketView.as_view(), name='select_bucket'),
    path('step2/', FileUploadView.as_view(), name='file_upload'),
    path('step3/', ProcessView.as_view(), name='process'),
    # path('file_upload/', FileUploadView.as_view(), name='file_upload'),
    # path('process/', ProcessView.as_view(), name='process')
]