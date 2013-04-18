from django.http import HttpResponse
import render
from models import Topic

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

def main(request,  site="vacloud.us"):    
    v = {}
    topics = []
    for t in Topic.objects.all():
        t.intensity = get_rating(t.resourceorigins.all().count(), 'intensity') 
        t.impact = get_rating(t.capabilities.all().count(), 'impact') 
        t.relevance = get_rating(t.imperatives.all().count(), 'relevance') 
        topics.append(t)
    
    template_file = '/main/esil.html'
    v['topics'] = topics
    v['nav'] = 'esil'

    return HttpResponse(render.load(template_file, v))