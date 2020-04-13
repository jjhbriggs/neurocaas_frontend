from django.urls import path, include
from .views import *


urlpatterns = [
    path('', HomeView.as_view(template_name="main/home.html"), name="home"),

    # demo 2
    path('demo/', MainView.as_view(), name='demo2'),
    path('get_user_files/', UserFilesView.as_view(), name='get_user_files'),
    path('get_results/', ResultView.as_view(), name='get_results')
]
