from django.urls import path
from . import views

urlpatterns = [
    path('racecard/', views.races, name='races'),
    ]

