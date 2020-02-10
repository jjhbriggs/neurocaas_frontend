from django.urls import path, include
from .views import *

urlpatterns = [
    path('detail', AccountDetailView.as_view(), name='account_detail')
]
