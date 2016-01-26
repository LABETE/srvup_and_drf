from django.conf.urls import include, url
from django.contrib import admin

from .views import NotificationListView, ReadRedirectView, AjaxNotificationsView

urlpatterns = [
    url(r'^$', view=NotificationListView.as_view(), name="list"),
    url(r'^read/(?P<pk>\d+)/$', ReadRedirectView.as_view(), name='read'),
    url(r'^ajax_notifications/$', AjaxNotificationsView.as_view(), name='ajax_notifications'),
]
