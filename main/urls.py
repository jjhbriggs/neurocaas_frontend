from django.urls import path, include
from .views import *


urlpatterns = [
    path('', IntroView.as_view(), name='intro'),
    path('home/', HomeView.as_view(template_name="main/home.html"), name="home"),
    path('intro/<int:id>', AnalysisIntroView.as_view(), name='analysis_intro'),
    path('history/<int:ana_id>', JobHistoryListView.as_view(), name='job_history'),
    path('history/<int:ana_id>/<str:job_id>', JobDetailView.as_view(), name='job_detail'),
    path('analysis_qa/', QAView.as_view(), name='analysis_qa'),
    path('analyses/', AnalysisListView.as_view(), name='analyses'),

    path('process/<int:id>', ProcessView.as_view(), name='process'),
    path('get_user_files/<int:ana_id>', UserFilesView.as_view(), name='get_user_files'),
    path('get_results/', ResultView.as_view(), name='get_results')
]
