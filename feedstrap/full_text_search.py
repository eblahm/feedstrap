import pysolr
from feedstrap import render
from feedstrap.models import Resource
from jinja2 import Environment, PackageLoader

def normalize(x):
    try:
        return str(x)
    except:
        try:
            return x.decode('utf8').encode('ascii', 'xmlcharrefreplace')
        except:
            return x.encode('ascii', 'xmlcharrefreplace')

def remove_control_characters(s):
    return "".join(c for c in s if ord(c) >= 32)


def doc_maker(db_obj):
    if db_obj.content is not None and db_obj.content != "":
        db_obj.content = normalize(db_obj.content)
        db_obj.content = remove_control_characters(db_obj.content)
    tags_list = sorted([t.name for t in db_obj.tags.all()])
    db_obj.tags_cont = ", ".join(tags_list)
    template_values = {'r':db_obj}
    text = render.load('search/index.html', template_values)
    text = normalize(text)
    doc = {"id": str(db_obj.pk), "content": text, "url": db_obj.link}
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
        q = Resource.objects.all()
        for r in q:
            print added
            docs.append(doc_maker(r))
            added += 1
        self.solr.add(docs)
        return {'deleted': deleted, 'added': added}
    def add_resource(self, r):
        solr = self.solr
        doc = doc_maker(r)
        solr.add([doc])
        return doc

    def delete_resource(self, resource_item):
        self.solr.delete(id=resource_item.pk)
        return 'deleted'
