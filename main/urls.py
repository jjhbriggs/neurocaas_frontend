from django.urls import path, include
from .views import *


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('upload/', FileUploadView.as_view(), name='file_upload'),
]