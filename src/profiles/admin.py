from django.contrib import admin

from .models import Profile, Relationship
from sorl.thumbnail.admin import AdminImageMixin


@admin.register(Profile)
class ProfileAdmin(AdminImageMixin, admin.ModelAdmin):
  list_display = ['user', 'first_name', 'last_name', 'bio']
  list_filter = ['created', 'updated']
  search_fields = ['first_name', 'last_name', 'user', 'bio', 'country']
  date_hierarchy = 'created'

admin.site.register(Relationship)