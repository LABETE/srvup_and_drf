from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import truncatechars
from users.models import User
from videos.models import Video


class CommentManager(models.Manager):

    def all(self):
        return super(CommentManager, self).filter(active=True).filter(parent=None)

    def recent(self):
        try:
            limit_to = settings.RECENT_COMMENT_NUMBER
        except:
            limit_to = 6
        return self.get_queryset().filter(active=True).filter(parent=None)[:limit_to]

    def create_comment(self, user=None, text=None, path=None, video=None, parent=None):
        if not text:
            raise ValueError("Must include text")
        if not path:
            raise ValueError("Must include a path when adding a comment")
        if not user:
            raise ValueError("Must include a user when adding a comment")

        comment = Comment(
            user=user,
            text=text,
            path=path
        )
        if video:
            comment.video = video
        if parent:
            comment.parent = parent
        comment.save(using=self._db)
        return comment


class Comment(models.Model):
    user = models.ForeignKey(User)
    parent = models.ForeignKey("self", null=True, blank=True)
    path = models.CharField(max_length=350)
    video = models.ForeignKey(Video, null=True, blank=True)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    active = models.BooleanField(default=True)

    objects = CommentManager()

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse("comments:detail", kwargs={"pk": self.pk})

    @property
    def get_comment(self):
        return self.text

    @property
    def get_preview(self):
        return truncatechars(self.text, 120)

    @property
    def is_child(self):
        if self.parent:
            return True
        else:
            return False

    @property
    def get_path(self):
        return self.path

    def get_children(self):
        if self.is_child:
            return None
        else:
            return Comment.objects.filter(parent=self).order_by("timestamp")

    def get_affected_users(self):
        comment_children = self.get_children()
        if comment_children:
            users = [self.user]
            for comment in comment_children:
                if comment.user not in users:
                    users.append(comment.user)
            return users
        return None
