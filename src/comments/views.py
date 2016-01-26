from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from braces.views import LoginRequiredMixin

from comments.models import Comment
from notifications.signals import notify

from videos.forms import CommentForm


class CommentDetailView(LoginRequiredMixin, FormView, DetailView):
    model = Comment
    form_class = CommentForm

    def get_context_data(self, *args, **kwargs):
        context = super(CommentDetailView, self).get_context_data(
            *args, **kwargs)
        context["comments"] = self.get_object().get_children()
        context["form"] = self.form_class
        return context

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            clean_text = form.cleaned_data["text"]
            Comment.objects.create_comment(
                user=self.request.user,
                text=clean_text,
                path=self.get_object().get_path,
                video=self.get_object().video,
                parent=self.get_object())
            affected_users = self.get_object().get_affected_users()
            #print(self.get_object().get)
            notify.send(self.request.user,
                        recipient=self.get_object().user,
                        action=self.get_object(),
                        target=self.get_object().video,
                        verb=u'commented',
                        affected_users=affected_users,
                        )
            messages.success(self.request, "Thank you for your comment")

            return HttpResponseRedirect(self.get_object().get_absolute_url())
        else:
            messages.error(self.request, "There was an error")
            return HttpResponseRedirect(self.get_object().get_absolute_url())
