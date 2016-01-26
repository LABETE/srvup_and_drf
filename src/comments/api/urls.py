from django.conf.urls import url

from .views import CommentCreateAPIView, CommentListAPIView, CommentRetrieveAPIView

urlpatterns = [
    url(r'^$', view=CommentListAPIView.as_view(), name="list_api"),
    url(r'^create/$', view=CommentCreateAPIView.as_view(), name="create_api"),
    url(r'^(?P<pk>\d+)/$', view=CommentRetrieveAPIView.as_view(), name="detail_api"),
]
