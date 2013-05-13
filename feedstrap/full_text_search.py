from ssg_site import pysolr
from feedstrap import render
from feedstrap.models import Resource
from jinja2 import Environment, PackageLoader

mpa = dict.fromkeys(range(32))
def doc_maker(db_obj):
    db_obj.content = db.obj.content.translate(mpa)
    tags_list = sorted([t.name for t in db_obj.tags.all()])
    db_obj.tags_cont = ", ".join(tags_list)
    template_values = {'r':db_obj}
    template_env = render.env
    template = template_env.get_template('/search/index.html')
    text = template.render(template_values)
    doc = {"id": db_obj.pk, "content": text, "url": db_obj.link}
    return doc

class solr_server():
    def __init__(self):
        self.solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)

    def reindex_all(self):
        current_docs = self.solr.search('*:*')
        deleted = 0
        for d in current_docs:
            self.solr.delete(id=d['id'])
            deleted += 1
        docs = []
        added = 0
        for r in Resource.objects.all():
            docs.append(doc_maker(r))
            added += 1
        self.solr.add(docs)
        return {'deleted': deleted, 'added': added}

    def add_resource(self, resource_item):
        self.solr.delete(id=resource_item.pk)
        doc = doc_maker(resource_item)
        self.solr.add([doc])
        return doc

    def delete_resource(self, resource_item):
        self.solr.delete(id=resource_item.pk)
        return 'deleted'
