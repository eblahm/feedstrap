from django.contrib import admin
from django.contrib.admin import widgets
from django import forms
from feedstrap.models import *

tag_type = [Tag, Report, Office]

#Imperative, Capability, ResourceOrigin,

# Topic, Feed,
# Resource, DeletedLink, Comment

class ResourceForm(forms.ModelForm):
    tags = forms.MultipleChoiceField(choices=generate_choices(Tag))
    feeds = forms.MultipleChoiceField(choices=generate_choices(Feed))
    topics = forms.MultipleChoiceField(choices=generate_choices(Topic))
    offices = forms.MultipleChoiceField(choices=generate_choices(Office))
    reports = forms.MultipleChoiceField(choices=generate_choices(Report))
    class Meta:
        model = Resource

class ResourceAdmin(admin.ModelAdmin):
    form = ResourceForm
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
    
    
for data_field in [Topic, ResourceOrigin, Imperative, Capability]:
    admin.site.register(data_field)