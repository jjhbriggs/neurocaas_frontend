from django.urls import path, include
from .views import *


urlpatterns = [
    path('', IntroView.as_view(), name='intro'),
    path('home/', HomeView.as_view(template_name="main/home.html"), name="home"),
    path('intro/', AnalysisIntroView.as_view(), name='analysis_intro'),

    # demo 2
    path('process/', ProcessView.as_view(), name='process'),
    path('get_user_files/', UserFilesView.as_view(), name='get_user_files'),
    path('get_results/', ResultView.as_view(), name='get_results')
]
