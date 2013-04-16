from django.contrib import admin
from django.contrib.admin import widgets
from feedstrap.models import *

tag_type = [Tag, Report, Office]

#Imperative, Capability, ResourceOrigin,

# Topic, Feed,
# Resource, DeletedLink, Comment

class ResourceAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    list_display = ('title','date')

admin.site.register(Resource, ResourceAdmin)


class FeedAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'url')

admin.site.register(Feed, FeedAdmin)

for i in tag_type:
    class AdminFormat(admin.ModelAdmin):
        list_display = ('name',)
    admin.site.register(i, AdminFormat)