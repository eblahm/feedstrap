import config
from django.http import HttpResponse
from datetime import datetime
import render
import home
import urllib
from models import Topic, Resource, Report

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
    filters = dict(request.GET.lists())
    v.update(home.apply_filter(filters))
    v.update(request.GET.dict())
    v['headline'] = 'Weekly Reads Database'
    v['subheadline'] = 'Prepared by Strategic Studies Group, Office of Policy'
    v['date'] = datetime.now().strftime('%x')
    
    conditions = []
    # for f in filters:
    #     if f != 's':
    #         condition = "%s=%s" % (f, urllib.quote(",".join(filters[f])))
    #         conditions.append(condition)
    v['show_more_url'] = "/weeklyreads/ajax/?" + "&".join(conditions)
    if site == 'ajax':
        template_file = '/main/weekly_reads/table_body.html'
    else:
        template_file = '/main/weekly_reads/sharepoint_view.html'
    return HttpResponse(render.load(template_file, v))
    
    # response = HttpResponse(content_type='application/msword')
    # response['Content-Disposition'] = 'attachment; filename="Weekly Read Export.html"'
    # ms_doc = render.load(template_file, v)
    # response.write(ms_doc)
    
    
    
    
