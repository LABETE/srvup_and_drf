"""srvup URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from srvup.views import HomeView, Contact
from srvup.api.views import HomeAPIView
from users.views import AccountTemplateView


urlpatterns = [
    url(r'^$', HomeView.as_view(), name="home"),
    url(r'^contact/$', Contact.as_view(), name="contact"),
    url(r'^account/$', AccountTemplateView.as_view(), name="account_profile"),
    url(r'^billing/', include("billing.urls", namespace="billing")),
    url(r'^categories/', include("videos.urls", namespace="categories")),
    url(r'^comments/', include("comments.urls", namespace="comments")),
    url(r'^notifications/', include("notifications.urls", namespace="notifications")),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/auth/token/$', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/categories/', include("videos.api.urls", namespace="category")),
    url(r'^api/comments/', include("comments.api.urls", namespace="comment")),
    url(r'^api/$', HomeAPIView.as_view(), name="home_api"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
