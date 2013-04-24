import render
from models import Topic, Resource, Report
from filter import apply_filter

from django.http import HttpResponse
from datetime import datetime


def get_rating(val, factor):
    rate_dic = {'intensity': (4, 10), 
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
    topics = []
    for t in Topic.objects.all():
        t.intensity = get_rating(t.resourceorigins.all().count(), 'intensity') 
        t.impact = get_rating(t.capabilities.all().count(), 'impact') 
        t.relevance = get_rating(t.imperatives.all().count(), 'relevance') 
        topics.append(t)
    v['topics'] = topics
    if site == 'sharepoint':
        template_file = '/main/esil/sharepoint_view.html'
    else:
        template_file = '/main/esil/main_view.html'
        v['nav'] = 'esil'  
    return HttpResponse(render.load(template_file, v))

def weeklyreads(request, site="sharepoint"):
    v = {}
    v.update(request.GET.dict())

    if len(request.GET.dict()) > 0:
        v.update(apply_filter(request))

    if site == 'export_to_word':
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
        template_file = '/main/weekly_reads/table_body.html'
        return HttpResponse(render.load(template_file, v))
    else:
        v['headline'] = 'Weekly Reads Database'
        template_file = '/main/weekly_reads/sharepoint_view.html'
        return HttpResponse(render.load(template_file, v))

    

    
    
    
    
