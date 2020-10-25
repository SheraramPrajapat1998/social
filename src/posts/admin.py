from django.contrib import admin

from .models import Post, Comment, Like
from sorl.thumbnail.admin import AdminImageMixin

@admin.register(Post)
class PostAdmin(AdminImageMixin, admin.ModelAdmin):
  list_display = ['author', 'draft', 'content']
  list_filter = ['updated', 'created', 'draft']
  date_hierarchy = 'created'

admin.site.register(Comment)
admin.site.register(Like)