from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.shortcuts import render
from django.views.generic.base import TemplateView

from analytics.models import PageView
from analytics.signals import page_view
from comments.models import Comment
from videos.models import Video, Category


class HomeView(TemplateView):

    template_name = "home.html"

    def get_context_data(self, *args, **kwargs):
        context = super(HomeView, self).get_context_data(*args, **kwargs)
        page_view.send(self.request.user,
                       page_path=self.request.get_full_path())
        if not self.request.user.is_authenticated():
            context["featured_videos"] = Video.objects.get_featured()
            context["featured_categories"] = Category.objects.get_featured()
        if self.request.user.is_authenticated():
            recent_views_objs = self.request.user.pageview_set.get_videos()
            recent_videos = []
            for video in recent_views_objs:
                if video.primary_object not in recent_videos:
                    recent_videos.append(video.primary_object)
            recent_comments = Comment.objects.recent()
            popular_videos = []
            video_type = ContentType.objects.get_for_model(Video)
            popular_videos_list = PageView.objects.filter(
                primary_content_type=video_type)\
                .values("primary_object_id")\
                .annotate(the_count=Count("primary_object_id"))\
                .order_by("-the_count")[:2]
            for item in popular_videos_list:
                popular_video = Video.objects.get(id=item["primary_object_id"])
                popular_videos.append(popular_video)
            random_videos = Video.objects.all().order_by("?")[:6]
            context["recent_videos"] = recent_videos
            context["recent_comments"] = recent_comments
            context["popular_videos"] = popular_videos
            context["random_videos"] = random_videos
        return context


class Contact(TemplateView):
    template_name = "contact.html"
