from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Video, Category, TaggedItem


admin.site.register(TaggedItem)


class TaggedItemInline(GenericTabularInline):
    model = TaggedItem
    extra = 1


class VideoAdmin(admin.ModelAdmin):
    inlines = [TaggedItemInline]
    list_display = ["__str__", "slug"]
    fields = ["title", "order", "embed_code",
        "share_message", "active",
        "featured", "free_preview",
        "category"]
    # prepopulated_fields = {
    #     "slug": ["title"]
    # }
    class Meta:
        model = Video


admin.site.register(Video, VideoAdmin)


class VideoInline(admin.TabularInline):
    model = Video
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    inlines = [VideoInline, TaggedItemInline]

admin.site.register(Category, CategoryAdmin)
