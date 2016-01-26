from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView



from analytics.signals import page_view
from comments.models import Comment
from notifications.signals import notify

from .forms import CommentForm
from .models import Video, Category


class VideoDetailView(FormView, DetailView):
    model = Video
    form_class = CommentForm

    def get(self, *args, **kwargs):
        cat = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        vid = get_object_or_404(Video, slug=self.kwargs['slug'], category=cat)
        if not self.request.user.is_authenticated() and not vid.has_preview():
            return redirect("billing:upgrade")
        return super(VideoDetailView, self).get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(VideoDetailView, self).get_context_data(
            *args, **kwargs)
        cat = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        vid = get_object_or_404(Video, slug=self.kwargs['slug'], category=cat)
        page_view.send(self.request.user,
                       page_path=self.request.get_full_path(),
                       primary_obj=vid,
                       secondary_obj=cat)
        context["comments"] = self.get_object().comment_set.all()
        context["form"] = self.form_class
        return context

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            parent_id = self.request.POST.get("parent_id")
            parent_comment = None
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                except:
                    parent_comment = None
            clean_text = form.cleaned_data["text"]
            new_comment = Comment.objects.create_comment(
                user=self.request.user,
                text=clean_text,
                path=self.request.get_full_path(),
                video=self.get_object(),
                parent=parent_comment)
            if parent_comment:
                comment = parent_comment
            else:
                comment = new_comment
            affected_users = comment.get_affected_users()
            notify.send(self.request.user,
                        recipient=comment.user,
                        action=comment,
                        target=new_comment.video,
                        affected_users=affected_users,
                        verb=u'commented',
                        )
            messages.success(self.request, "Thank you for your comment")
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        else:
            messages.error(self.request, "There was an error")
            return HttpResponseRedirect(self.get_object().get_absolute_url())


class VideoListView(ListView):
    queryset = Video.objects.all()

    def get_queryset(self, *args, **kwargs):
        cat = get_object_or_404(Category, slug=self.kwargs['slug'])
        qs = Video.objects.get_by_category(self.kwargs['slug'])
        page_view.send(self.request.user,
                       page_path=self.request.get_full_path(),
                       primary_obj=cat)
        return qs


class CategoryListView(ListView):
    model = Category
