from django.urls import path
from . import views
from django.views.generic import RedirectView
from .views import register, user_login, user_logout


urlpatterns = [
    path('', views.about, name='about'),
    path('racecard/', views.racecard, name='racecard'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', user_logout, name='logout'),
    ]

