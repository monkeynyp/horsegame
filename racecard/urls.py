from django.urls import path,include
from . import views
from django.views.generic import RedirectView
from .views import register, user_login, user_logout
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.recent_article, name='recent_article'),
    path('racecard/', views.racecard, name='racecard'),
    path('view_by_member/', views.view_by_member, name='view_by_member'),
    path('blog/', views.recent_article, name='recent_article'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path('send_article_email/', views.send_article_email, name='send_article_email'),
    path('contact/', views.contact, name='contact'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('privacy/', views.privacy, name='privacy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('facebookfeed/', views.facebook_feed, name='facebook_feed'),
    path('like_article/<int:article_id>/', views.like_article, name='like_article'),

    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('submittips/',views.submit_tips, name='submit_tips'),
    path('member/', views.member, name='member'),
    ]

