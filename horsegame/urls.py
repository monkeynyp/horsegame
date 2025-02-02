"""
URL configuration for horsegame project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.views.i18n import set_language
from django.http import HttpResponsePermanentRedirect

def redirect_to_www(request):
    """Redirect non-www traffic to www.monkeyforecast.com"""
    if request.get_host() == "monkeyforecast.com":
        return HttpResponsePermanentRedirect(f"https://www.monkeyforecast.com{request.path}")
    return HttpResponsePermanentRedirect(f"https://www.monkeyforecast.com/")


urlpatterns = [
    path('', redirect_to_www),
    path("admin/", admin.site.urls),
    path('', include('racecard.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('i18n/', set_language, name='set_language'),
    path('comments/', include('django_comments.urls')),

]
