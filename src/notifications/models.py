from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from .signals import notify


class NotificationQuerySet(models.query.QuerySet):

    def get_user(self, user):
        return self.filter(recipient=user)

    def read(self):
        return self.filter(read=True)

    def unread(self):
        return self.filter(read=False)


class NotificationManager(models.Manager):

    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def all_read(self, user):
        return self.get_queryset().get_user(user).read()

    def all_unread(self, user):
        return self.get_queryset().get_user(user).unread()

    def all_for_user(self, user):
        return self.get_queryset().get_user(user)

    def recent_for_user(self, user):
        return self.get_queryset().unread().get_user(user)[:5]


class Notification(models.Model):
    sender_content_type = models.ForeignKey(
        ContentType, related_name='notify_sender')
    sender_object_id = models.PositiveIntegerField()
    sender_object = GenericForeignKey(
        "sender_content_type", "sender_object_id")

    verb = models.CharField(max_length=255)

    action_content_type = models.ForeignKey(ContentType,
                                            related_name='notify_action',
                                            null=True, blank=True)
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey(
        "action_content_type", "action_object_id")

    target_content_type = models.ForeignKey(ContentType,
                                            related_name='notify_target',
                                            null=True, blank=True)
    target_object_id = models.PositiveIntegerField(null=True, blank=True)
    target_object = GenericForeignKey(
        "target_content_type", "target_object_id")
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='notifications')
    read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = NotificationManager()

    def __str__(self):
        if self.target_object and self.action_object:
            html_text = "<a href='{0}'>{1}</a>".format(
                reverse("notifications:read",
                        kwargs={"pk": self.pk}), self.action_object)
            return "{0} {1} {2} on {3} comment".format(
                self.sender_object,
                self.verb,
                html_text,
                self.target_object)
        if self.target_object:
            target_url = self.target_object.get_absolute_url()
            html_text = "<a href='{0}'>{1}</a>".format(
                target_url, self.target_object)
            return "{0} {1} {2}".format(
                self.sender_object,
                self.verb,
                html_text)
        return "{0} {1}".format(
            self.sender_object,
            self.verb)

    @property
    def get_notification_link(self):
        if self.action_object:
            html_text = "<a href='{0}'>{1} {2} {3} {4}</a>".format(
                reverse("notifications:read",
                        kwargs={"pk": self.pk}),
                self.sender_object,
                self.verb,
                self.action_object,
                self.target_object)
            return html_text
        html_text = "<a href='{0}'>{1} {2}</a>".format(
                reverse("notifications:list"),
                self.sender_object,
                self.verb)
        return html_text


def new_notification(sender, **kwargs):
    kwargs.pop('signal', None)
    recipient = kwargs.pop('recipient')
    verb = kwargs.pop('verb')
    affected_users = kwargs.pop("affected_users", None)
    if affected_users:
        for user in affected_users:
            if user != sender:
                new_note = Notification(
                    recipient=user,
                    verb=verb,
                    sender_content_type=ContentType.objects.get_for_model(sender),
                    sender_object_id=sender.id,
                )
                for option in ("target", "action"):
                    try:
                        obj = kwargs[option]
                        if obj:
                            setattr(new_note, "{0}_content_type".format(
                                option), ContentType.objects.get_for_model(obj))
                            setattr(new_note, "{0}_object_id".format(option), obj.id)
                    except:
                        pass
                new_note.save()
    else:
        if recipient != sender:
            new_note = Notification(
                recipient=recipient,
                verb=verb,
                sender_content_type=ContentType.objects.get_for_model(sender),
                sender_object_id=sender.id,
            )
            for option in ("target", "action"):
                try:
                    obj = kwargs[option]
                    if obj:
                        setattr(new_note, "{0}_content_type".format(
                            option), ContentType.objects.get_for_model(obj))
                        setattr(new_note, "{0}_object_id".format(option), obj.id)
                except:
                    pass
            new_note.save()

notify.connect(new_notification)
