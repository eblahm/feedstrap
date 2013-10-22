from feedstrap.search import solr_server
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        solr = solr_server()
        counts = solr.reindex_all()
        print 'good'


