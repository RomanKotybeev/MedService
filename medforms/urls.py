from django.urls import path
from .views import *

# app_name = 'medforms'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('edit/<str:slug>', UpdateMedService.as_view(), name='edit'),
]