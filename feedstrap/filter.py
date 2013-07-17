from ssg_site import config
import models
from models import Resource, ResourceForm, Topic
from django.contrib.auth.models import User
from datetime import datetime

import render
from django.http import HttpResponse
from django.core.context_processors import csrf
from django import forms
from django.db.models import Q

import pysolr
import operator

from edit import get_tags

class Filter():
    def __init__(self, name, qstring, qmodel=models.Resource):
        self.name = name
        self.qstring = qstring
        self.qmodel = qmodel
    def get_displayed_filter(self, filtered_value):
        if self.name in ['reports', 'offices', 'esil', 'feeds']:
            q = self.qmodel.objects.get(pk=filtered_value)
            displayed_filter = q.name
        else:
            displayed_filter = filtered_value
        return displayed_filter

filters = {
    'tags': Filter('tags', 'tags__name', models.Tag),
    'person': Filter('firstname', 'feeds__user__first_name', models.Feed),
    'feeds': Filter('feeds', 'feeds__pk', models.Feed),
    'esil': Filter('esil', 'topics__pk', models.Topic),
    'dateto': Filter('dateto', 'date__lte'),
    'datefrom': Filter('datefrom', 'date__gte'),
    'report': Filter('report', 'reports__name', models.Report),
    'office': Filter('office', 'offices__name', models.Office),
}

labels = {
    'person': 'background-color: orange;',
    'report': 'background-color: #2D6987;',
    'tags': 'background-color: #0088CC',
    'office': 'background-color: green',
    'term': 'background-color: #ffd62f;',
    'feeds': 'background-color: orange',
    'esil': 'background-color: red',
}

class FilterForm(forms.Form):
    tags = forms.CharField(max_length=100)
    datefrom = forms.DateField('%Y-%m-%d')
    dateto = forms.DateField('%Y-%m-%d')
    esil = forms.ChoiceField(choices=models.generate_choices(models.Topic))
    office = forms.ChoiceField(choices=models.generate_choices(models.Office,'name', 'name'))
    person = forms.ChoiceField(choices=models.generate_choices(User, 'first_name', 'first_name'))
    feeds = forms.ChoiceField(choices=models.generate_choices(models.Feed))
    report = forms.ChoiceField(choices=models.generate_choices(models.Report, 'name', 'name'))

def apply_filter(request, q=Resource.objects.all().order_by("-date"), per_page_limit=config.per_page_limit, slice=True):
    v = {}
    applied_filters = request.GET.dict()
    applied_filters.pop('csrfmiddlewaretoken', None)
    applied_filters.pop('field', None)
    start_offset = applied_filters.get('s', '0')
    start_offset = int(start_offset)

    text_search = applied_filters.get('term', None)
    if len(applied_filters) == 0:
        pass
    elif text_search != None and config.solr_enabled:
        solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
        srt = 'score desc'
        # if '/rss' in request.path:
        #     srt = 'id desc'
        results = solr.search(text_search, **{'hl': 'true',
                                            'hl.fl': '*',
                                            'fl': '*,score',
                                            'rows': 50,
                                            'sort': srt,
                                            'hl.fragsize': 200,
                                            'hl.snippets': 3})
        search_snippets = {}
        hl = results.highlighting
        pk_list = []
        for r in results:
            search_snippets[int(r['id'])] = hl[r['id']]
            pk_list.append(r['id'])
        v.update({'search_snippets': search_snippets})

        if applied_filters.get('report', None) is not None:
            q = Resource.objects.all()
            q = q.filter(pk__in=pk_list)
            q = q.filter(reports__name=applied_filters.get('report'))
        else:
            q = []
            for p in pk_list:
                pk = int(str(p))
                lookup = Resource.objects.filter(pk=pk)
                if lookup.count() > 0:
                    q.append(lookup.get())
    else:
        q = Resource.objects.all()
        sorted_filters = sorted(applied_filters.iteritems(), key=operator.itemgetter(0))
        and_queries = None
        all_qs = []
        for i in sorted_filters:
            if i[0] == 's':
                continue
            field = i[0].split('_')[-1]
            value = i[1]
            if field != 'andor':
                filter = filters[str(field)]
                if field in ['dateto', 'datefrom']:
                    value = datetime.strptime(value, '%Y-%m-%d')
                x = Q((filter.qstring, value))
                if and_queries == None:
                    and_queries = q.filter(x)
                else:
                    and_queries &= q.filter(x)
            if field == 'andor':
                if value == "OR":
                    if and_queries != None:
                        all_qs.append(and_queries)
                        and_queries = None
        if and_queries != None:
            all_qs.append(and_queries)
        if len(all_qs) == 1:
            q = all_qs[0]
        elif len(all_qs) > 1:
            q = all_qs[0]
            for oq in all_qs[1:]:
                q |= oq
        q = q.distinct().order_by('-date')

    if slice:
        if start_offset == 0:
            q = q[:per_page_limit]
        else:
            limit = start_offset + per_page_limit
            q = q[start_offset:limit]

    if text_search != None:
        count = len(q)
    else:
        count = q.count()
    if count == per_page_limit:
        v['next_offset'] = start_offset + per_page_limit
    v['results'] = q

    next_perams = request.GET.copy()
    next_offset = str(v.get('next_offset', '0'))
    next_perams.__setitem__('s', next_offset)
    v['show_more_perams'] = next_perams.urlencode()
    return v

def generate_filter_tags(request):
    data = request.GET.dict()
    data.pop('csrfmiddlewaretoken', None)
    data.pop('field', None)

    filter_tags = []
    i = 1
    for tag in data:
        new_perameters = request.GET.copy()
        new_perameters.pop(tag)
        new_perameters = new_perameters.urlencode()
        filter_value = data[tag]
        field_name = tag.split("_")[-1]
        i = tag.split("_")[0]
        if field_name == 'andor':
            if filter_value == "OR":
                class ft:
                    css = labels.get(field_name, 'background-color: black')
                    name = "OR"
                    link = "/q?" + new_perameters
                    index = i + 'a'
            else:
                continue
        elif field_name == 'term':
            class ft:
                css = labels.get(field_name, 'background-color: black')
                name = "%s: %s" % (field_name, filter_value)
                link = "/q?" + new_perameters
                index = '1'
        else:
            class ft:
                css = labels.get(field_name, 'background-color: black')
                name = "%s: %s" % (field_name, filters[field_name].get_displayed_filter(filter_value))
                link = "/q?" + new_perameters
                index = i + 'b'
        filter_tags.append(ft)
    filter_tags = sorted(filter_tags, key=lambda ft: ft.index)
    return filter_tags

def main(request):
    if request.method == "GET":
        perams = request.GET.dict()
        v = {}
        v['all_tags'] = get_tags()
        if len(perams) == 0:
            v.update(csrf(request))
            template_file = '/main/forms/filter.html'
            v['filter_count'] = 1
            return render.response(request, template_file, v)
        else:
            v['filter_count'] = perams['filter_count']
            if perams['a'] == 'new':
                template_file = '/main/forms/filter_row.html'
                return render.response(request, template_file, v)
            elif perams['a'] == 'field':
                f = FilterForm()
                new_input = str(f[perams['selected']])
                return HttpResponse(new_input)
