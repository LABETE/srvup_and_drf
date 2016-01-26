from rest_framework import serializers, viewsets, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from comments.serializers import CommentSerializer
from .models import Video, Category


class VideoHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        kwargs = {
            "cat_slug": obj.category.slug,
            "vid_slug": obj.slug
        }
        return self.reverse(view_name,
                            kwargs=kwargs, request=request, format=format)


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    url = VideoHyperlinkedIdentityField(view_name="category:video_detail_api")
    category_url = serializers.CharField(source="category.get_absolute_url", read_only=True)
    comment_set = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = (
            "url",
            "id",
            "slug",
            "title",
            "order",
            "embed_code",
            "share_message",
            "comment_set",
            "free_preview",
            'category_url',
            "timestamp",
        )


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="category:detail_api", lookup_field="slug")
    video_set = VideoSerializer(many=True)

    class Meta:
        model = Category
        fields = (
            "url",
            "id",
            "title",
            "description",
            "image",
            "video_set",
            "slug",
        )
