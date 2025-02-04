# schedule/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_section/', views.add_section, name='add_section'),
    path('add_teacher/', views.add_teacher, name='add_teacher'),
    path('generate_schedule/', views.generate_schedule, name='generate_schedule'),
    path('download_schedule/', views.download_schedule, name='download_schedule'),
]
