from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.about, name='about'),
    path('racecard/', views.racecard, name='racecard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    ]

