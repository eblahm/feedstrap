from django.db import models
from django.forms import ModelForm
import full_text_search

def generate_choices(model, displayed_value='name', real_value="pk"):
    options = (("", ""),)
    for r in model.objects.all():
        options += ((str(getattr(r, real_value)), getattr(r, displayed_value)),)
    return options

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


origin_choices = (
    ('Office', 'Office'),
    ('Departmental', 'Departmental'),
    ('Governmental', 'Governmental'),
    ('Non-Governmental', 'Non-Governmental'),
    ('Other', 'Other'),
)

class ResourceOrigin(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=origin_choices)


class Topic(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField()
    resourceorigins = models.ManyToManyField(ResourceOrigin, null=True, blank=True)
    imperatives = models.ManyToManyField(Imperative, null=True, blank=True)
    capabilities = models.ManyToManyField(Capability, null=True, blank=True)


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
    link = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    relevance = models.TextField(null=True, blank=True)
    content = models.TextField(blank=True)
    offices = models.ManyToManyField(Office, null=True, blank=True)
    feeds = models.ManyToManyField(Feed, null=True, blank=True)
    topics = models.ManyToManyField(Topic, null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    reports = models.ManyToManyField(Report, null=True, blank=True)
    def save(self):
        solr = full_text_search.solr_server()
        super(Resource, self).save()
        solr.add_resource(self)
        return self

class ResourceForm(ModelForm):
    class Meta:
        model = Resource


class DeletedLink(models.Model):
    link = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now=True)
    
