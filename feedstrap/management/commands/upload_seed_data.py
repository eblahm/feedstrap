from feedstrap.models import Imperative, Capability, ResourceOrigin, Feed
from django.core.management.base import BaseCommand, CommandError
import config
import csv
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        def get_full_path(short_name):
            return config.app_root + '/feedstrap/seed_data/' + file
        file_to_model = [('capabilities.csv', Capability), ('imperatives.csv', Imperative), ('resource origins.csv', ResourceOrigin)]
        for file, model in file_to_model:
            with open(get_full_path(file), 'rb') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    new = model(category=row[0], name=row[1])
                    new.save()
                self.stdout.write("%s was added to the Database!" % (file))


        with open(get_full_path('feeds.csv'), 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                new = Feed(url = row[0],
                    name = row[1],
                    owner = row[2],
                    description = row[3],
                    # offices = row[0],
                    # topics = row[0],
                    # tags = row[0],
                    # reports = row[0],
                    last_updated = datetime.now(),)
                new.save()
