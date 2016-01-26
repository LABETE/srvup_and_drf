from urllib.request import quote
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.text import slugify


from .utils import get_vid_for_direction


class VideoQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)

    def free_preview(self):
        return self.filter(free_preview=True)

    def embed_code(self):
        return self.filter(embed_code__isnull=False).exclude(embed_code__iexact="")

    def category(self, slug):
        cat = Category.objects.get(slug=slug)
        return self.filter(category=cat.id)


class VideoManager(models.Manager):

    def get_queryset(self):
        return VideoQuerySet(self.model, using=self._db)

    def get_featured(self):
        return self.get_queryset().featured().active()

    def get_by_category(self, slug):
        return self.get_queryset().active().embed_code().category(slug=slug)

    def all(self):
        return self.get_queryset().active().embed_code()


DEFAULT_MESSAGE = "Check this awesome video."


class Video(models.Model):
    title = models.CharField(max_length=120)
    embed_code = models.CharField(max_length=500, null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    share_message = models.TextField(max_length=140, default=DEFAULT_MESSAGE)
    tags = GenericRelation("TaggedItem", null=True, blank=True)
    active = models.BooleanField(default=True)
    slug = models.SlugField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    free_preview = models.BooleanField(default=False)
    category = models.ForeignKey("Category")
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False, null=True)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True, null=True)

    objects = VideoManager()

    class Meta:
        ordering = ['order', 'timestamp']
        unique_together = ('slug', 'category')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("categories:video_detail", kwargs={"cat_slug": self.category.slug, "slug": self.slug})

    def get_share_link(self):
        full_url = "{0}{1}".format(settings.FULL_DOMAIN_NAME, self.get_absolute_url())
        return quote("{0} {1}".format(self.share_message, full_url))

    def get_next_url(self):
        video = get_vid_for_direction(self, "next")
        if video:
            return video.get_absolute_url()
        return None

    def get_previous_url(self):
        video = get_vid_for_direction(self, "previous")
        if video:
            return video.get_absolute_url()
        return None

    def has_preview(self):
        if self.free_preview:
            return True
        return False


def video_post_save_receiver(sender, instance, created, *args, **kwargs):
    slug_title = slugify(instance.title)
    if created:
        slug_exists = Video.objects.filter(slug=slug_title)
        if slug_exists:
            new_slug = "{0} {1}".format(instance.title, instance.id)
            instance.slug = slugify(new_slug)
            instance.save()
        else:
            instance.slug = slug_title
            instance.save()


post_save.connect(video_post_save_receiver, sender=Video)


class CategoryQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(active=True)

    def featured(self):
        return self.filter(featured=True)


class CategoryManager(models.Manager):

    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def get_featured(self):
        return self.get_queryset().featured().active()

    def all(self):
        return self.get_queryset().active()


class Category(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    tags = GenericRelation("TaggedItem", null=True, blank=True)
    slug = models.SlugField(unique=True, default="abc")
    active = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    objects = CategoryManager()

    class Meta:
        ordering = ['title', 'timestamp']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("categories:detail", kwargs={"slug": self.slug})

    def get_image_url(self):
        return "{0}{1}".format(settings.MEDIA_URL, self.image)


def category_post_save_receiver(sender, instance, created, *args, **kwargs):
    slug_title = slugify(instance.title)
    if created:
        slug_exists = Category.objects.filter(slug=slug_title)
        if slug_exists:
            new_slug = "{0} {1}".format(instance.title, instance.id)
            instance.slug = slugify(new_slug)
            instance.save()
        else:
            instance.slug = slug_title
            instance.save()


post_save.connect(category_post_save_receiver, sender=Category)

TAG_CHOICES = (
    ("python", "python"),
    ("django", "django"),
    ("css", "css"),
    ("bootstrap", "bootstrap"),
)


class TaggedItem(models.Model):
    tag = models.SlugField(choices=TAG_CHOICES)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return self.tag
