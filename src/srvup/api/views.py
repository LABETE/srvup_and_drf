from rest_framework.views import APIView
from rest_framework.reverse import reverse as api_reverse
from rest_framework.response import Response

from comments.models import Comment
from videos.models import Category


class HomeAPIView(APIView):

    def get(self, request, format=None):
        data = {
            "categories": {
                "url": api_reverse("category:list_api", request=request),
                "count": Category.objects.all().count()
            },
            "comments": {
                "url": api_reverse("comment:list_api", request=request),
                "count": Comment.objects.all().count()
            }
        }
        return Response(data)
