from django.contrib import admin
from django.contrib.admin import widgets
from django import forms
from feedstrap.models import *

## Resource ##
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
    list_display = ('title','date_added')

admin.site.register(Resource, ResourceAdmin)

## Feed ##
class FeedForm(forms.ModelForm):
    tags = forms.MultipleChoiceField(choices=generate_choices(Tag))
    feeds = forms.MultipleChoiceField(choices=generate_choices(Feed))
    topics = forms.MultipleChoiceField(choices=generate_choices(Topic))
    offices = forms.MultipleChoiceField(choices=generate_choices(Office))
    reports = forms.MultipleChoiceField(choices=generate_choices(Report))
    class Meta:
        model = Feed
        
class FeedAdmin(admin.ModelAdmin):
    form = FeedForm
    list_display = ('name', 'owner', 'url')

admin.site.register(Feed, FeedAdmin)

## Topic ##
class TopicForm(forms.ModelForm):
    resourceorigins = forms.MultipleChoiceField(choices=generate_choices(ResourceOrigin))
    imperatives = forms.MultipleChoiceField(choices=generate_choices(Imperative))
    capabilities = forms.MultipleChoiceField(choices=generate_choices(Capability))

    class Meta:
        model = Topic
        
class TopicAdmin(admin.ModelAdmin):
    form = TopicForm
    ordering = ('name',)
    list_display = ('name',)

admin.site.register(Topic, TopicAdmin)




## Tag, Report, Office ##
for simple_model in [Tag, Office, Report]:
    class simple_admin(admin.ModelAdmin):
        ordering = ('name',)
        list_display = ('name',)
    admin.site.register(simple_model, simple_admin)

## Capabilities, Imperatives, Resource Origins ##
for simple_model in [Capability, ResourceOrigin, Imperative]:
    class simple_admin(admin.ModelAdmin):
        ordering = ('category', 'name')
        list_display = ('name', 'category')
    admin.site.register(simple_model, simple_admin)
        


class LinkLogAdmin(admin.ModelAdmin):
    ordering = ('date',)
    list_display = ('link', 'date')

admin.site.register(LinkLog, LinkLogAdmin)
























