from feedstrap.models import *
from feedstrap import models
from django.core.management.base import BaseCommand, CommandError
from ssg_site import config
import csv
from datetime import datetime
import pytz



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ignored_values = ["", "null", "None", None, "Top 10 Report", "alchemy call fail", "error", "error1","error2","error3","error4", "-"]

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

        reader = csv.reader(open(get_full_path('feeds.csv'), 'rb'))
        for row in reader:
            if Feed.objects.filter(url=row[0]).count() == 0:
                new = Feed(url = row[0],
                    name = row[1],
                    owner = row[2],
                    description = row[3],
                    last_updated = datetime.now(),)
                new.save()
                office = Office.objects.get(name=row[4])
                new.offices.add(office)
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
            self.stdout.write("topics.csv was added to the Database!\n")

        topic_names = {'agtzfnZhdG9vbGJveHIOCxIGdG9waWNzGJucFgw': 'Millennial Impact',
                       'agtzfnZhdG9vbGJveHIOCxIGdG9waWNzGO2rFgw': 'The Changing Nature of Veteran Entitlement',
                       'agtzfnZhdG9vbGJveHIOCxIGdG9waWNzGNWzFgw': 'Dr. Siri',
                       'agtzfnZhdG9vbGJveHIOCxIGdG9waWNzGMOJFww': 'The Challenge of a Mobile Enterprise',}

        reader = csv.reader(open(get_full_path('resources.csv'), 'rb'))
        write_count = 0
        def normalize(s):
            if s in ignored_values:
                return None
            else:
                return s
        for row in reader:
            try:
                if row[3] == "null" or row[3] == "":
                    feed = Feed.objects.get(owner='Matt')
                else:
                    feed = Feed.objects.get(url=row[3])
            except:
                continue

            duplicate_test = Resource.objects.filter(link=row[5])
            if duplicate_test.count() == 1:
                rec = Resource.objects.get(link=row[5])
                if feed in rec.feeds.all():
                    continue
            else:
                x = 0
                if row[1] == 'null':
                    row[1] = '2012-02-17T00:00:00'
                for r in row:
                    if r == "null":
                        row[x] = ""
                    x += 1
                x = 0
                text = row[8]
                if len(text) < 10:
                    text = ""
                rec = Resource(
                    date = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.utc),
                    date_added = datetime.strptime(row[1], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.utc),
                    title = row[4],
                    link = row[5],
                    description = normalize(row[6]),
                    relevance = normalize(row[7]),
                    content = normalize(text),
                )
                rec.save()


            if feed not in rec.feeds.all():
                rec.feeds.add(feed)
            else:
                continue

            topics = []
            for topic_dbk in row[10].split(","):
                if topic_dbk not in ["", 'null']:
                    topics.append(topic_names[topic_dbk.strip()])
            tags = row[9].split(",")
            offices = [row[2]]
            reports = row[11].split(",")

            for i in tags:
                if i.strip() in ignored_values or len(i) >= 50:
                    pass
                else:
                    try:
                        obj = Tag.objects.get(name=i.strip())
                    except:
                        obj = Tag(name=i.strip())
                        obj.save()
                    if obj not in rec.tags.all():
                        rec.tags.add(obj)

            for i in topics:
                if i.strip() in ignored_values:
                    pass
                else:
                    try:
                        obj = Topic.objects.get(name=i.strip())
                    except:
                        assert False
                    if obj not in rec.topics.all():
                        rec.topics.add(obj)

            for i in offices:
                if i.strip() in ignored_values:
                    pass
                else:
                    if i.strip() == "Front Office":
                        O = "AS"
                    else:
                        O = i
                    try:
                        obj = Office.objects.get(name=O.strip())
                    except:
                        obj = Office(name=O.strip())
                        obj.save()
                    if obj not in rec.offices.all():
                        rec.offices.add(obj)

            for i in reports:
                if i.strip() in ignored_values:
                    pass
                else:
                    try:
                        obj = Report.objects.get(name=i.strip())
                    except:
                        obj = Report(name=i.strip())
                        obj.save()
                    if obj not in rec.reports.all():
                        rec.reports.add(obj)
            rec.save()
            logq = models.LinkLog.objects.filter(link=rec.link)
            if logq.count() > 0:
                log = logq.get()
            else:
                log = models.LinkLog(link=rec.link)
                log.save()
            for f in rec.feeds.all():
                log.feeds.add(f)
            log.save()
            write_count += 1
            self.stdout.write("%i Resource added!\n" % (write_count))


