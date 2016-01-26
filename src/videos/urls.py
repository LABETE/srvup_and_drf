from django.conf.urls import include, url
from django.contrib import admin

from .views import CategoryListView, VideoDetailView, VideoListView

urlpatterns = [
    url(r'^$', view=CategoryListView.as_view(), name="list"),
    url(r'^(?P<slug>[\w-]+)/$', view=VideoListView.as_view(), name="detail"),
    url(r'^(?P<cat_slug>[\w-]+)/(?P<slug>[\w-]+)/$', view=VideoDetailView.as_view(), name="video_detail"),
]
