from django.conf.urls import include, url
from django.contrib import admin

from .views import CommentDetailView

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', view=CommentDetailView.as_view(), name="detail"),
]
