from ssg_site import pysolr
from feedstrap import render
from feedstrap import full_text_search
from jinja2 import Environment, PackageLoader
from feedstrap.models import Resource, Tag
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        solr = full_text_search.solr_server()
        counts = solr.reindex_all()
        self.stdout.write('You reindexed %i' % (counts['added']))

