from feedstrap.models import Feed, Topic
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for f in Feed.objects.all():
            q = User.objects.filter(first_name=f.owner)
            if q.count() >= 1:
                f.user = q[0]
            else:
                f.user = None
            f.save()
            self.stdout.write("%s --> %s" % (f.name, f.user))