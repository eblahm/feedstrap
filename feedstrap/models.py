from django.db import models

office_choices = (
    ('SSG', 'Strategic Stuides Group'),
    ('PAS', 'Policy Analysis Service'),
    ('SPS', 'Strategic Planning Service'),
    ('AS', 'Front Office'),
)

class Tag(models.Model):
    name = models.CharField(max_length=50)

class Report(models.Model):
    name = models.CharField(max_length=50)

class Option(models.Model):
    name = models.CharField(max_length=50)

class Imperative(models.Model):
    name = models.CharField(max_length=50)

class Capability(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=500)

class ResourceOrigin(models.Model):
    name = models.CharField(max_length=50)

class Topic(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField()
    options = models.ManyToManyField(Option,null=True, blank=True)
    resource_origins = models.ManyToManyField(ResourceOrigin,null=True, blank=True)
    imperatives = models.ManyToManyField(Imperative,null=True, blank=True)
    capabilities = models.ManyToManyField(Capability,null=True, blank=True)

class Office(models.Model):
    name = models.CharField(max_length=50, choices=office_choices)

class Feed(models.Model):
    url = models.CharField(max_length=500)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)

    description = models.CharField(max_length=500)

    offices = models.ManyToManyField(Office, null=True, blank=True)
    topics = models.ManyToManyField(Topic, null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    reports = models.ManyToManyField(Report, null=True, blank=True)

    last_updated = models.DateTimeField()

class Resource(models.Model):
    # for versioning
    date = models.DateTimeField()
    date_added = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=500)
    link = models.CharField(max_length=500, unique=True)

    description = models.TextField()
    relevance = models.TextField()
    content = models.TextField(blank=True)

    offices = models.ManyToManyField(Office,null=True, blank=True)
    feeds = models.ManyToManyField(Feed, null=True, blank=True)
    topics = models.ManyToManyField(Topic, null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    reports = models.ManyToManyField(Report, null=True, blank=True)

class DeletedLink(models.Model):
    link = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    name = models.CharField(max_length=500)
    email = models.EmailField()
    org = models.CharField(max_length=100,null=True, blank=True)
    comment = models.TextField()
    date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField()

allow_admin_for = [Tag, Report, Office, Option, Imperative, Capability, ResourceOrigin, Topic, Feed, Resource, DeletedLink, Comment]