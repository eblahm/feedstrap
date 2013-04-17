from ssg_site import pysolr
from feedstrap import render
from jinja2 import Environment, PackageLoader
from feedstrap.models import Resource, Tag
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
        current_docs = solr.search('*:*')
        for d in current_docs:
            solr.delete(id=d['id'])
        template_env = render.env
        docs = []
        for r in Resource.objects.all():
            tags_list = sorted([t.name for t in r.tags.all()])
            r.tags_cont = ", ".join(tags_list)
            template_values = {'r':r}
            template = template_env.get_template('/search/index.html')
            text = template.render(template_values)
            doc = {"id": r.pk, "content": text, "url": r.link}
            docs.append(doc)
        solr.add(docs)
        self.stdout.write('You did it!')

