from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from django import forms
from feedstrap.models import *
from django.core.cache import cache
from tinymce.widgets import TinyMCE
from django.core import mail


## Static Page ##
class StaticPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))
    class Meta:
        model = StaticPage

class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    form = StaticPageForm

admin.site.register(StaticPage, StaticPageAdmin)

## Resource ##
class ResourceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        for k in ['tags', 'topics', 'offices', 'reports']:
            self.fields[k].required = False
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
    def __init__(self, *args, **kwargs):
        super(FeedForm, self).__init__(*args, **kwargs)
        for k in ['tags', 'topics', 'offices', 'reports']:
            self.fields[k].required = False
    tags = forms.MultipleChoiceField(choices=generate_choices(Tag))
    topics = forms.MultipleChoiceField(choices=generate_choices(Topic))
    offices = forms.MultipleChoiceField(choices=generate_choices(Office))
    reports = forms.MultipleChoiceField(choices=generate_choices(Report))
    class Meta:
        model = Feed

class FeedAdmin(admin.ModelAdmin):
    form = FeedForm
    list_display = ('name', 'user', 'url')

admin.site.register(Feed, FeedAdmin)

## Topic ##
class TopicForm(forms.ModelForm):
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
for simple_model in [Capability, Imperative]:
    class simple_admin(admin.ModelAdmin):
        ordering = ('category', 'name')
        list_display = ('name', 'category')
    admin.site.register(simple_model, simple_admin)


class InviteeAdmin(admin.ModelAdmin):

    ordering = ('date',)
    list_display = ('email', 'is_email_sent', 'has_accepted', 'date', 'url_secret')
    exclude = ('url_secret', 'is_email_sent')

    change_list_template = 'admin/invitee/change_list.html'
    def changelist_view(self, request, extra_context={}):
        return super(InviteeAdmin, self).changelist_view(request, extra_context=extra_context)

    def send_email_invitation(self, request, queryset):
        email_connection = mail.get_connection()
        email_connection.open()
        messages = []

        for i in queryset:
            messages.append(i.invite(connection=email_connection))

        email_connection.send_messages(messages)
        email_connection.close()

        self.message_user(request, "%i email invitation sent!" % len(messages))
    actions = [send_email_invitation]

admin.site.register(Invitee, InviteeAdmin)

class SidebarLinkAdmin(admin.ModelAdmin):
    ordering = ('position',)
    list_display = ('name', 'parameters', 'position')
    def save_model(self, request, obj, form, change):
        cache.clear()
        obj.save()
admin.site.register(SidebarLink, SidebarLinkAdmin)
    



class PostItForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super(PostItForm, self).__init__(*args, **kwargs)
    #     for k in ['sidebar_links', 'office']:
    #         self.fields[k].required = False
    # sidebar_links = forms.MultipleChoiceField(choices=generate_choices(SidebarLink))
    class Meta:
        model = PostIt

class PostItInline(admin.StackedInline):
    model = PostIt
    form = PostItForm
    can_delete = False
    verbose_name_plural = 'Additional Fields'
    exclude = ('feed', 'sidebar_links')
    list_display = ('office',)


class UserAdmin(UserAdmin):
    inlines = (PostItInline, )

    
    def allow_to_see_full_ESIL(self, request, queryset):
        group, created = Group.objects.get_or_create(name='Can see full ESIL')
        if created:
            esil_view_all = Permission.objects.get(codename='view_all')
            group.permissions.add(esil_view_all)
            group.save()
            
        x = 0
        for u in queryset:
            u.groups.add(group)
            u.save()
            x += 1

        self.message_user(request, "%i users were granted access to the full ESIL!" % x)
        
    actions = [allow_to_see_full_ESIL]
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)




