from rest_framework import generics, mixins

from ..models import Comment
from ..permissions import IsOwnerOrReadOnly
from ..serializers import CommentSerializer, CommentUpdateSerializer, CommentCreateSerializer


class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer


class CommentRetrieveAPIView(mixins.DestroyModelMixin, mixins.UpdateModelMixin, generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentUpdateSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def put(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        qs = Comment.objects.filter(pk__gt=0)
        return qs


class CommentListAPIView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
