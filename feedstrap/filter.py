import config
import models
from models import Resource, ResourceForm, Topic

from django.shortcuts import render
from django.http import HttpResponse
from django.http import QueryDict
from django import forms

from ssg_site import pysolr
import re



def apply_filter(request, q=Resource.objects.all(), per_page_limit=config.per_page_limit):
    v = {}
    query_filters = dict(request.GET.lists())
    for filter in query_filters:
        filter_value = query_filters[filter]
        if filter[-3:] == 'tag':
            mm_rec = models.Tag.objects.filter(name__in=filter_value)
            q = q.filter(tags__in=mm_rec)
        elif filter[-6:] == 'report':
            mm_rec = models.Report.objects.filter(name__in=filter_value)
            q = q.filter(reports__in=mm_rec)
        elif filter[-6:] == 'office':
            mm_rec = models.Office.objects.filter(name__in=filter_value)
            mm_rec = models.Feed.objects.filter(offices__in=mm_rec)
            q = q.filter(feeds__in=mm_rec)
    text_search = " ".join(query_filters.get('term', ""))
    if text_search.strip() != "":
        solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
        results = solr.search(text_search, **{'hl': 'true',
                                            'hl.fl': '*',
                                            'hl.fragsize': 200,
                                            'hl.snippets': 3})
        search_snippets = {}
        hl = results.highlighting
        pk_list = []
        for r in results:
            search_snippets[int(r['id'])] = hl[r['id']]
            pk_list.append(r['id'])
        v.update({'search_snippets': search_snippets})
        q = q.filter(pk__in=pk_list)
    else:
        q = q.order_by('-date')
    start_offset = query_filters.get('s', ['0'])
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


class FilterForm(forms.Form):
    search_term = forms.CharField(max_length=100)
    tags = forms.CharField(max_length=100)
    date_from = forms.DateField('%Y-%m-%d')
    date_to = forms.DateField('%Y-%m-%d')
    esil = forms.MultipleChoiceField(choices=models.generate_choices(models.Topic))
    office = forms.MultipleChoiceField(choices=models.generate_choices(models.Office))
    individual = forms.MultipleChoiceField(choices=models.generate_choices(models.Feed, 'owner'))
    report = forms.MultipleChoiceField(choices=models.generate_choices(models.Report))

def generate_filter_tags(request):
    labels = {
        'report': 'background-color: #2D6987;',
        'tag': 'background-color: #0088CC',
        'office': 'background-color: green',
        'term': 'background-color: #ffd62f;',
        'feed': 'background-color: orange',
        'esil': 'background-color: red',
    }
    filter_tags = []
    data = dict(request.GET.lists())
    for tag in data:
        new_perameters = request.GET.copy()
        new_perameters.pop(tag)
        new_perameters = new_perameters.urlencode()
        filter_value = ", ".join(data[tag])
        # pattern = '%s=.+&|%s=.+$' % (tag, tag)
        # modified_perams = re.sub(pattern, "", perams)
        # modified_perams = "/q?" + modified_perams
        # modified_perams.replace("?&", "?").replace("&&", "&")
        class ft:
            css = labels[tag]
            name = "%s: %s" % (tag, filter_value)
            link = "/q?" + new_perameters
        filter_tags.append(ft)
    return filter_tags

def main(request):
    if request.method == "GET":
        perams = request.GET.dict()
        v = {}
        if len(perams) == 0:
            template_file = config.app_root + '/feedstrap/templates/main/forms/filter.html'
            form = FilterForm()
            return render(request, template_file, {'form': form, 'foo':'foo'})
        else:
            foo = True
            return HttpResponse('fail')
