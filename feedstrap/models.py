from django.db import models

office_choices = (
    ('SSG', 'Strategic Stuides Group'),
    ('PAS', 'Policy Analysis Service'),
    ('SPS', 'Strategic Planning Service'),
    ('AS', 'Front Office'),
)

class Tag(models.Model):
    name = models.CharField(max_length=50)

class Keyword(models.Model):
    name = models.CharField(max_length=50)

class Concept(models.Model):
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

class Data_source(models.Model):
    name = models.CharField(max_length=50)

class Topic(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField()
    options = models.ManyToManyField(Option)
    data_sources = models.ManyToManyField(Data_source)
    imperatives = models.ManyToManyField(Imperative)
    capabilities = models.ManyToManyField(Capability)

class Feed(models.Model):
    url = models.CharField(max_length=500)
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100)
    office = models.CharField(max_length=50, choices=office_choices)
    description = models.CharField(max_length=500)

    esil = models.ManyToManyField(Topic)
    tags = models.ManyToManyField(Tag)
    keywords = models.ManyToManyField(Keyword)
    concepts = models.ManyToManyField(Concept)
    reports = models.ManyToManyField(Report)

    last_updated = models.DateTimeField()

class Resource(models.Model):
    # for versioning
    date = models.DateTimeField()
    date_added = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField()
    office = models.CharField(max_length=50, choices=office_choices)
    title = models.CharField(max_length=500)
    link = models.CharField(max_length=500, unique=True)

    description = models.TextField()
    relevance = models.TextField()
    content = models.TextField()

    feed = models.ForeignKey(Feed)
    esil = models.ManyToManyField(Topic)
    tags = models.ManyToManyField(Tag)
    keywords = models.ManyToManyField(Keyword)
    concepts = models.ManyToManyField(Concept)
    reports = models.ManyToManyField(Report)

class Deleted_link(models.Model):
    link = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now=True)

class Comment(models.Model):
    name = models.CharField(max_length=500)
    email = models.EmailField()
    org = models.CharField(max_length=500)
    comment = models.TextField()
    date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField()

allow_admin_for = [Tag, Keyword, Concept, Report, Option, Imperative, Capability, Data_source, Topic, Feed, Resource, Deleted_link, Comment]