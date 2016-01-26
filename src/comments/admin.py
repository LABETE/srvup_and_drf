from django.contrib import admin

from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ["__str__", "text"]

    class Meta:
        model = Comment

admin.site.register(Comment, CommentAdmin)
