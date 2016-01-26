from django.core.urlresolvers import reverse
from django.http import JsonResponse, Http404
from django.views.generic.base import RedirectView, View
from django.views.generic.list import ListView

from braces.views import LoginRequiredMixin

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    pattern_name = "comments:detail"

    def get_queryset(self):
        return Notification.objects.all_for_user(self.request.user)


class ReadRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get(self, *args, **kwargs):
        qs = Notification.objects.filter(pk=kwargs['pk'])
        # qs = get_object_or_404(Notification, pk=kwargs['pk'])
        qs.update(read=True)
        try:
            pk = qs.values('action_object_id')[0]['action_object_id']
        except:
            raise Http404
        self.url = reverse(
                "comments:detail",
                kwargs={"pk": pk}
            )
        return super(ReadRedirectView, self).get(*args, **kwargs)


class AjaxNotificationsView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        notes = []
        #notifications = Notification.objects.all()
        notifications = Notification.objects.recent_for_user(self.request.user)
        for note in notifications:
            notes.append(str(note.get_notification_link))
        data = {
            "notifications": notes,
            "count": notifications.count()
        }
        return JsonResponse(data)
