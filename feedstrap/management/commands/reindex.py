from feedstrap import full_text_search
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        solr = full_text_search.solr_server()
        counts = solr.reindex_all()
        print 'good'
        #self.stdout.write('You reindexed %s') % (str(counts['added']))


