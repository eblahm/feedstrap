from HTMLParser import HTMLParser
from feedstrap.models import Resource 

def redo_titles():
    parser = HTMLParser()
    for r in Resource.objects.all():
        r.title = parser.unescape(r.title).encode('utf-8', 'ignore')
        r.save()
        print str(r.pk)
    return 'done!'