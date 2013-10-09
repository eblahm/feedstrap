from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from HTMLParser import HTMLParser

from tinymce.models import HTMLField
from feedstrap import config

import hashlib


def generate_choices(model, displayed_value='name', real_value="pk"):
    options = ()
    for r in model.objects.all():
        options += ((str(getattr(r, real_value)), getattr(r, displayed_value)),)
    return tuple(sorted(set(options), key=lambda opt: opt[1]))


class Tag(models.Model):
    name = models.CharField(max_length=50)


class Report(models.Model):
    name = models.CharField(max_length=50)

imperative_choices = (
    ('Be A Pro-Active and Agile Institution', 'Be A Pro-Active and Agile Institution'),
    ('Be Recognized for Providing a Quality Experience', 'Be Recognized for Providing a Quality Experience'),
    ('Be a Trusted Partner', 'Be a Trusted Partner'),
)

class Imperative(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=imperative_choices)

capability_choices = (
    ('Provide Services for Veterans and Eligible Beneficiaries', 'Provide Services for Veterans and Eligible Beneficiaries'),
    ('Support Delivery of Services', 'Support Delivery of Services'),
    ('Manage Government Resources', 'Manage Government Resources'),
)

class Capability(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=capability_choices)



class Topic(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField()
    imperatives = models.ManyToManyField(Imperative, null=True, blank=True)
    capabilities = models.ManyToManyField(Capability, null=True, blank=True)
    attachment = models.FileField(upload_to="final", null=True, blank=True)
    published = models.BooleanField()
    
    class Meta:
        permissions = (
            ("view_all", "Can see all the ESIL topics"),
        )


class Office(models.Model):
    name = models.CharField(max_length=200)
    acronym = models.CharField(max_length=50, default=None, null=True)
    
    def __unicode__(self):
        return self.name


class Feed(models.Model):
    url = models.CharField(max_length=500)
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, blank=True, null=True)
    description = models.CharField(max_length=500)
    offices = models.ManyToManyField(Office, blank=True)
    topics = models.ManyToManyField(Topic, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
    reports = models.ManyToManyField(Report, blank=True, null=True)
    last_updated = models.DateTimeField()
    fetching = models.BooleanField()
    
    def __unicode__(self):
        return self.name


class Resource(models.Model):
    date = models.DateTimeField()
    date_added = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=500)
    link = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    relevance = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    offices = models.ManyToManyField(Office, null=True, blank=True)
    feeds = models.ManyToManyField(Feed, null=True, blank=True)
    topics = models.ManyToManyField(Topic, null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    reports = models.ManyToManyField(Report, null=True, blank=True)

    def save(self):
        cache.clear()
        super(Resource, self).save()
        if config.solr_enabled:
            import full_text_search
            solr = full_text_search.solr_server()
            x = solr.add_resource(self)
        return self


class ResourceForm(ModelForm):
    class Meta:
        model = Resource


class LinkLog(models.Model):
    link = models.CharField(max_length=500)
    feeds = models.ManyToManyField(Feed, null=True, blank=True)
    date = models.DateTimeField(auto_now=True)


class SidebarLink(models.Model):
    name = models.CharField(max_length=100)
    parameters = models.CharField(max_length=500, blank=True)
    position = models.IntegerField()


class StaticPage(models.Model):
    slug = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    content = HTMLField()
    position = models.IntegerField()
    published = models.BooleanField()


class PostIt(models.Model):
    user = models.OneToOneField(User)
    feed = models.OneToOneField(Feed)
    office = models.ForeignKey(Office, blank=True, null=True)
    sidebar_links = models.ManyToManyField(SidebarLink, blank=True, null=True)
    
    class Meta:
        verbose_name = "User Extended"
        verbose_name_plural = "User Extended"
    
class Invitee(models.Model):
    date = models.DateTimeField(auto_now=True)
    url_secret = models.CharField(max_length=500)
    email = models.EmailField(max_length=254)
    has_accepted = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)

    def save(self):
        if not self.url_secret:
            self.url_secret = hashlib.md5(self.email).hexdigest()
        super(Invitee, self).save()
        return self
    
    def invite(self, connection=None):

        editable_template = StaticPage.objects.filter(slug = 'invite')
        if not editable_template:
            text = render_to_string('admin/invitee/email.txt', {'url_secret': self.url_secret})
            html = None
        else:
            raw_text = []
            class text_only(HTMLParser):
                def handle_data(self, data):
                    raw_text.append(data)

            cxt = Context({'url_secret': self.url_secret})
            editable_template = editable_template.get()

            html = Template(editable_template.content).render(cxt)

            text_parser = text_only()
            text_parser.feed(editable_template.content)
            raw_text = "".join(raw_text)
            text = Template(raw_text).render(cxt)


        email = EmailMultiAlternatives(
            "The Strategic Studies Group Invites you to Sign Up for FeedStrap!",
            text,
            settings.DEFAULT_FROM_EMAIL, [self.email], 
            connection=connection,
            alternatives=""
        )
        if html: email.attach_alternative(html, "text/html")
        if not connection: email.send()

        self.is_email_sent = True
        self.save()
        return email
    
