from django.contrib.auth import get_user_model

from rest_framework import serializers, permissions
from rest_framework.reverse import reverse

from .models import Comment

User = get_user_model()


class CommentVideoHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):

    def get_url(self, obj, view_name, request, format):
        video = None
        kwargs = {} 
        if obj.is_child and obj.parent.video:
            video = obj.parent.video
        elif not obj.is_child and obj.video:
            video = obj.video
        if video:
            kwargs = {
                "cat_slug": video.category.slug,
                "vid_slug": video.slug
            }
            return reverse(view_name, kwargs=kwargs, request=request, format=format)
        return None


class CommentUpdateSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "text",
        )


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            "user",
            "text",
            "video",
            "parent",
        )


class ChildCommentSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "text",
        )


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="comment:detail_api")
    user = serializers.CharField(source="user.username", read_only=True)
    children = serializers.SerializerMethodField(read_only=True)
    video = CommentVideoHyperlinkedIdentityField("category:video_detail_api")

    class Meta:
        model = Comment
        fields = (
            "url",
            "id",
            "user",
            "children",
            "video",
            "text",
        )

    def get_children(self, instance):
        queryset = Comment.objects.filter(parent=instance)
        serializer = ChildCommentSerializer(queryset, context={"request": instance}, many=True)
        return serializer.data


