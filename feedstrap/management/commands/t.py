from feedstrap.models import Resource, Topic
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        x = 0
        for t in Topic.objects.all():
            t.delete()
            x += 1
        self.stdout.write(str(x))