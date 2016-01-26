from django.conf.urls import url

from .views import (
    CategoryListAPIView, CategoryRetrieveAPIView, VideoRetrieveAPIView)

urlpatterns = [
    url(r'^$', view=CategoryListAPIView.as_view(), name="list_api"),
    url(r'^(?P<slug>[\w-]+)/$',
        view=CategoryRetrieveAPIView.as_view(), name="detail_api"),
    url(r'^(?P<cat_slug>[\w-]+)/(?P<vid_slug>[\w-]+)/$',
        view=VideoRetrieveAPIView.as_view(), name="video_detail_api"),
]
