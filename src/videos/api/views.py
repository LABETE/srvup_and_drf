from django.shortcuts import get_object_or_404

from rest_framework import generics

from ..models import Video, Category
from ..permissions import IsMember
from ..serializers import CategorySerializer, VideoSerializer


class VideoRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsMember]

    def get_object(self):
        cat_slug = self.kwargs["cat_slug"]
        vid_slug = self.kwargs["vid_slug"]
        cat = get_object_or_404(Category, slug=cat_slug)
        obj = get_object_or_404(Video, category=cat, slug=vid_slug)
        return obj


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_object(self):
        slug = self.kwargs["slug"]
        obj = get_object_or_404(Category, slug=slug)
        return obj

