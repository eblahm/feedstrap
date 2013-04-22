from feedstrap.models import *
from django.core.management.base import BaseCommand, CommandError
import config
import csv
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        def get_full_path(short_name):
            return config.app_root + '/feedstrap/seed_data/' + short_name
        file_to_model = [('capabilities.csv', Capability),
                         ('imperatives.csv', Imperative),
                         ('resource origins.csv', ResourceOrigin),
                         ('offices.csv', Office),
                         ('reports.csv', Report)]
        for file, model in file_to_model:
            if model.objects.all().count() == 0:
                with open(get_full_path(file), 'rb') as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        if len(row) == 2:
                            new = model(category=row[0].strip(), name=row[1].strip())
                        elif len(row) == 1:
                            new = model(name=row[0].strip())
                        new.save()
                    self.stdout.write("%s was added to the Database!\n" % (file))

        if Feed.objects.all().count() == 0:
            reader = csv.reader(open(get_full_path('feeds.csv'), 'rb'))
            for row in reader:
                self.stdout.write(str(row))
                if len(row) > 1:
                    new = Feed(url = row[0],
                        name = row[1],
                        owner = row[2],
                        description = row[3],
                        last_updated = datetime.now(),)
                    new.save()
                    new.offices = Office.objects.get(name=row[4]),
                    new.reports = Report.objects.get(name=row[5]),
                        # topics = row[0],
                        # tags = row[0],

                    new.save()
                    self.stdout.write("feeds.csv was added to the Database!\n")

        if Topic.objects.all().count() == 0:
            reader = csv.reader(open(get_full_path('topics.csv'), 'rb'))
            for row in reader:
                capabilities = []
                imperatives = []
                for c in row[3].split('|'):
                    djobj = Capability.objects.get(name=c)
                    self.stdout.write(djobj.name + "\n")
                    capabilities.append(djobj)
                for i in row[2].split('|'):
                    djobj = Imperative.objects.get(name=i)
                    self.stdout.write(djobj.name + "\n")
                    imperatives.append(djobj)
                new = Topic(name=row[0],
                            description=row[1],)
                new.save()
                new.capabilities = capabilities
                new.imperatives = imperatives
                new.save()