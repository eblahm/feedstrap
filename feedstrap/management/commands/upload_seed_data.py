from feedstrap.models import Imperative, Capability, ResourceOrigin
from django.core.management.base import BaseCommand, CommandError
import config
import csv


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        file_to_model = [('capabilities.csv', Capability), ('imperatives.csv', Imperative), ('resource origins.csv', ResourceOrigin)]
        for file, model in file_to_model:
            full_path = config.app_root + '/feedstrap/seed_data/' + file
            with open(full_path, 'rb') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    new = model(category=row[0], name=row[1])
                    new.save()
                self.stdout.write("%s was added to the Database!" % (file))

