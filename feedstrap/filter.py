import config
import models
from models import Resource, ResourceForm, Topic

import render
from django.http import HttpResponse
from django.http import QueryDict
from django.core.context_processors import csrf
from django import forms
from django.db.models import Q

from ssg_site import pysolr
import re
import operator



def apply_filter(request, q=Resource.objects.all(), per_page_limit=config.per_page_limit):
    v = {}
    filters = request.GET.dict()
    sorted_filters = sorted(filters.iteritems(), key=operator.itemgetter(0))
    q_filters = []
    qset = []
    for i in sorted_filters:
        if i[0] in ['csrfmiddlewaretoken', 'field', 's']:
            continue
        field = i[0].split('_')[-1]
        value = i[1]
        if field != 'andor':
            x = (field, value)
            qset.append(Q(x))
        if field == 'andor':
            if value == "OR":
                q_filters.append(reduce(operator.and_, qset))
                qset = []
    q_filters.append(reduce(operator.and_, qset))
    if len(q_filters) > 1:
        q = Resource.objects.filter(reduce(operator.or_, q_filters))
    else:
        q = Resource.objects.filter(reduce(operator.and_, qset))

    # query_filters = dict(request.GET.lists())
    # for filter in query_filters:
    #     filter_value = query_filters[filter]
    #     if filter[-3:] == 'tag':
    #         mm_rec = models.Tag.objects.filter(name__in=filter_value)
    #         q = q.filter(tags__in=mm_rec)
    #     elif filter[-6:] == 'report':
    #         mm_rec = models.Report.objects.filter(name__in=filter_value)
    #         q = q.filter(reports__in=mm_rec)
    #     elif filter[-6:] == 'office':
    #         mm_rec = models.Office.objects.filter(name__in=filter_value)
    #         mm_rec = models.Feed.objects.filter(offices__in=mm_rec)
    #         q = q.filter(feeds__in=mm_rec)
    # text_search = " ".join(query_filters.get('term', ""))
    # if text_search.strip() != "":
    #     solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
    #     results = solr.search(text_search, **{'hl': 'true',
    #                                         'hl.fl': '*',
    #                                         'hl.fragsize': 200,
    #                                         'hl.snippets': 3})
    #     search_snippets = {}
    #     hl = results.highlighting
    #     pk_list = []
    #     for r in results:
    #         search_snippets[int(r['id'])] = hl[r['id']]
    #         pk_list.append(r['id'])
    #     v.update({'search_snippets': search_snippets})
    #     q = q.filter(pk__in=pk_list)
    # else:
    #     q = q.order_by('-date')

    start_offset = filters.get('s', ['0'])
    start_offset = int(start_offset[0])
    if start_offset == 0:
        q = q[:config.per_page_limit]
    else:
        limit = start_offset + per_page_limit
        q = q[start_offset:limit]

    if q.count() == per_page_limit:
        v['next_offset'] = start_offset + per_page_limit
    v['results'] = q

    next_perams = request.GET.urlencode()
    next_perams = re.sub('[&s|s]=[0-9]{,5}', "", next_perams)
    next_perams += "&s=" + str(v.get('next_offset', '0'))
    v['show_more_perams'] = next_perams
    return v

def generate_choices(model, field='name'):
    options = (("", ""),)
    for r in model.objects.all():
        options += ((str(r.pk), getattr(r, field)),)
    return options

class FilterForm(forms.Form):
    tags = forms.CharField(max_length=100)
    date_from = forms.DateField('%Y-%m-%d')
    date_to = forms.DateField('%Y-%m-%d')
    esil = forms.ChoiceField(choices=models.generate_choices(models.Topic))
    offices = forms.ChoiceField(choices=models.generate_choices(models.Office))
    person = forms.ChoiceField(choices=models.generate_choices(models.Feed, 'owner'))
    feeds = forms.ChoiceField(choices=models.generate_choices(models.Feed))
    reports = forms.ChoiceField(choices=models.generate_choices(models.Report))

def generate_filter_tags(request):
    labels = {
        'reports': 'background-color: #2D6987;',
        'tags': 'background-color: #0088CC',
        'offices': 'background-color: green',
        'term': 'background-color: #ffd62f;',
        'feeds': 'background-color: orange',
        'esil': 'background-color: red',
    }
    filter_tags = []
    data = request.GET.dict()
    for i in request.GET.dict():
        if i in ['csrfmiddlewaretoken', 'field', 's']:
            data.pop(i)
        elif i.split("_")[-1] == 'andor':
            data.pop(i)
    for tag in data:
        new_perameters = request.GET.copy()
        new_perameters.pop(tag)
        new_perameters = new_perameters.urlencode()
        filter_value = data[tag]
        field_name = tag.split("_")[-1]
        if field_name in ['reports', 'feeds', 'offices', 'topics']:
            rec = getattr(models, field_name.title()[:-1]).objects.get(pk=filter_value)
            filter_value = rec.name
        class ft:
            css = labels.get(field_name, 'background-color: white')
            name = "%s: %s" % (field_name, filter_value)
            link = "/q?" + new_perameters
        filter_tags.append(ft)
    return filter_tags

def main(request):
    if request.method == "GET":
        perams = request.GET.dict()
        v = {}
        if len(perams) == 0:
            v.update(csrf(request))
            template_file = '/main/forms/filter.html'
            v['filter_count'] = 1
            return HttpResponse(render.load(template_file, v))
        else:
            v['filter_count'] = perams['filter_count']
            if perams['a'] == 'new':
                template_file = '/main/forms/filter_row.html'
                return HttpResponse(render.load(template_file, v))
            elif perams['a'] == 'field':
                f = FilterForm()
                new_input = str(f[perams['selected']])
                return HttpResponse(new_input)
    # if request.method == "POST":
    #     filters = request.POST.dict()
    #     sorted_filters = sorted(filters.iteritems(), key=operator.itemgetter(0))
    #     q_filters = []
    #     qset = []
    #     for i in sorted_filters:
    #         if i[0] in ['csrfmiddlewaretoken', 'field']:
    #             continue
    #         field = i[0].split('_')[-1]
    #         value = i[1]
    #         if field != 'andor':
    #             x = (field, value)
    #             qset.append(Q(x))
    #         if field == 'andor':
    #             if value == "OR":
    #                 q_filters.append(reduce(operator.and_, qset))
    #                 qset = []
    #     q_filters.append(reduce(operator.and_, qset))
    #     if len(q_filters) > 1:
    #         q = Resource.objects.filter(reduce(operator.or_, q_filters))
    #     else:
    #         q = Resource.objects.filter(reduce(operator.and_, qset))
    #     return HttpResponse(test)
