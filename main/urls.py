from django.urls import path, include
from .views import *
from django.conf.urls import url
from django.conf import settings

urlpatterns = [
    path('', IntroView.as_view(), name='intro'),
    path('home/', HomeView.as_view(template_name="main/home.html"), name="home"),
    path('analyses/', AnalysisListView.as_view(), name='analyses'),
    path('analysis/<int:ana_id>', AnalysisIntroView.as_view(), name='analysis_intro'),
    path('freq_qa/', QAView.as_view(), name='frequent_qa'),
    path('history/<int:ana_id>', JobListView.as_view(), name='job_history'),
    path('history/<int:ana_id>/<str:job_id>', JobDetailView.as_view(), name='job_detail'),
    path('files/<int:ana_id>/', FilesView.as_view(), name='file_view'),

    path('process/<int:ana_id>', ProcessView.as_view(), name='process'),
    path('user_files/<int:ana_id>', UserFilesView.as_view(), name='get_user_files'),
    path('results/<int:ana_id>', ResultView.as_view(), name='get_results'),

    # ================================
    path('test/', TestView.as_view(), name='test_page')
]
