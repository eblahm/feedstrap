import render
from models import Topic, Resource, Report
from filter import apply_filter

from django.http import HttpResponse, HttpResponseRedirect

from datetime import datetime
import csv
import urllib

def en(s):
    if isinstance(s, unicode):
        return s.encode('ascii', 'xmlcharrefreplace')
    else:
        return str(s)

def get_rating(val, factor):
    rate_dic = {'intensity': (15, 30),
                'relevance': (4, 10),
                'impact':(3, 8),}
    if val >= 0:
        button = '<span class="label">LOW</span>'
    if val >= rate_dic[factor][0]:
        button = '<span class="label label-warning">MED</span>'
    if val >= rate_dic[factor][1]:
        button = '<span class="label label-important">HIGH</span>'
    return button

def esil(request,  site="vacloud.us"):
    v = {'site':site}
    v['nav'] = 'esil'
    v['auth'] = request.user.is_authenticated()
    if v['auth']:
        selected = request.GET.get('k', None)
        if selected != None:
            topic = Topic.objects.get(pk=int(str(selected)))
            v['site'] = request.GET.dict().get('site', "vacloud.us")
            mm_fields = ['imperatives', 'capabilities']
            for i in mm_fields:
                mm_rec = getattr(topic, i)
                mapping = {}
                for mm_item in mm_rec.all().order_by('name'):
                    try:
                        index = mapping[mm_item.category]
                    except:
                        mapping[mm_item.category] = []
                        index = mapping[mm_item.category]
                    if mm_item.name not in index:
                        index.append(mm_item.name)
                v[i] = mapping
            rsearch = Resource.objects.filter(topics=topic).order_by('-date')
            topic.intensity = get_rating(rsearch.count(), 'intensity')
            topic.impact = get_rating(topic.capabilities.all().count(), 'impact')
            topic.relevance = get_rating(topic.imperatives.all().count(), 'relevance')
            v['topic'] = topic
            v['resources'] = rsearch
            v['get_url'] = request.GET.urlencode()
            return render.response(request, "/main/esil/topic_card.html", v)
        else:
            topics = []
            if v['auth'] == True:
                q = Topic.objects.all()
            else:
                q = Topic.objects.filter(published=True)
            for t in q.order_by('-attachment', 'name'):
                rsearch = Resource.objects.filter(topics=t)
                t.intensity = get_rating(rsearch.count(), 'intensity')
                t.impact = get_rating(t.capabilities.all().count(), 'impact')
                t.relevance = get_rating(t.imperatives.all().count(), 'relevance')
                topics.append(t)
            v['topics'] = topics
            if site == 'sharepoint':
                template_file = '/main/esil/sharepoint_view.html'
            else:
                template_file = '/main/esil/main_view.html'
    
            return render.response(request, template_file, v)
    else:
        return HttpResponseRedirect('/signin?redirect=%s' % (urllib.quote(request.get_full_path())))

def weeklyreads(request, site="sharepoint"):
    v = {'site': site}
    v.update(request.GET.dict())
    v['admin'] = request.user.is_authenticated()
    if site == 'export_to_word':
        v.update(apply_filter(request, per_page_limit=100))
        v['next_offset'] = False
        template_file = '/main/weekly_reads/export_view.html'
        v['headline'] = 'Weekly Reads Report'
        v['subheadline'] = 'Prepared by Strategic Studies Group, Office of Policy'
        v['date'] = datetime.now().strftime('%x')
        response = HttpResponse(content_type='application/msword')
        response['Content-Disposition'] = 'attachment; filename="%s SSG Weekly Reads.doc"' % (datetime.now().strftime('%y%m%d'))
        ms_doc = render.load(template_file, v)
        response.write(ms_doc)
        return response
    elif site == 'ajax':
        v.update(apply_filter(request))
        template_file = '/main/weekly_reads/table_body.html'
        return render.response(request, template_file, v)
    else:
        if len(request.GET.dict()) == 0:
            v['hide_table'] = True
        else:
            v.update(apply_filter(request))
        v['headline'] = 'Weekly Reads Database'
        template_file = '/main/weekly_reads/sharepoint_view.html'
        return render.response(request, template_file, v)

def export_csv(request):
    v = {}
    v.update(apply_filter(request, per_page_limit=5000))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search results.csv"'

    writer = csv.writer(response)
    header_row = ['feed urls', 'date', 'title', 'link', 'tags', 'description', 'relevance', 'content']
    writer.writerow(header_row)
    results = v['results']
    for rec in results:
        row = []
        row += [', '.join([en(f.url) for f in rec.feeds.all()])]
        row += [rec.date.strftime("%Y-%m-%dT%H:%M:%S")]
        row += [en(rec.title)]
        row += [en(rec.link)]
        row += [', '.join([en(t.name) for t in rec.tags.all()])]
        row += [en(rec.description)][:131071]
        row += [en(rec.relevance)][:131071]
        row += [en(rec.content)][:131071]
        writer.writerow(row)
    return response
