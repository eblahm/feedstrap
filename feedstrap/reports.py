import render
from models import Topic, Resource, Report
from filter import apply_filter

from django.http import HttpResponse

from datetime import datetime
import csv


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
    selected = request.GET.dict().get('k', None)
    if selected != None:
        topic = Topic.objects.get(pk=int(selected))
        mm_fields = ['imperatives', 'capabilities', 'resourceorigins']
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
        rsearch = Resource.objects.filter(topics=topic)
        topic.intensity = get_rating(rsearch.count(), 'intensity')
        topic.impact = get_rating(topic.capabilities.all().count(), 'impact')
        topic.relevance = get_rating(topic.imperatives.all().count(), 'relevance')
        v['topic'] = topic
        v['resources'] = rsearch
        v['get_url'] = request.GET.urlencode()
        return HttpResponse(render.load("/main/esil/topic_card.html", v))
    else:
        topics = []
        for t in Topic.objects.all():
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

        return HttpResponse(render.load(template_file, v))

def weeklyreads(request, site="sharepoint"):
    v = {}
    v.update(request.GET.dict())

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
        return HttpResponse(render.load(template_file, v))
    else:
        if len(request.GET.dict()) == 0:
            v['hide_table'] = True
        else:
            v.update(apply_filter(request))
        v['headline'] = 'Weekly Reads Database'
        template_file = '/main/weekly_reads/sharepoint_view.html'
        return HttpResponse(render.load(template_file, v))

def export_csv(request):
    v = {}
    v.update(apply_filter(request, per_page_limit=500))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search resulsts.csv"'

    writer = csv.writer(response)
    header_row = [f.name for f in Resource._meta.fields]
    header_row.remove('content')
    writer.writerow(header_row)
    results = v['results'].values()
    for rec in results:
        row = []
        for field in header_row:
            row.append(rec[field])
        writer.writerow(row)
    return response








