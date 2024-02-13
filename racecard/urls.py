from django.urls import path,include
from . import views
from django.views.generic import RedirectView
from .views import register, user_login, user_logout
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.about, name='about'),
    path('racecard/', views.racecard, name='racecard'),
    path('blog/', views.recent_article, name='recent_article'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', user_logout, name='logout'),
    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('submittips/',views.submit_tips, name='submit_tips'),
    path('member/', views.member, name='member'),
    ]

