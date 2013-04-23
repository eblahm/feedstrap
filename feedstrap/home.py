import config
import re
from django.http import HttpResponse
from models import Resource, ResourceForm, Topic
import models
import render
from datetime import datetime
# from ssg_site import pysolr  # , markdown

def text_search(term, query=Resource.objects.all()):
    solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
    results = solr.search(" ".join(perameters['term']), **{'hl': 'true',
                                        'hl.fl': '*',
                                        'hl.fragsize': 200,
                                        'hl.snippets': 3})
    search_snippets = {}
    hl = results.highlighting
    pk_list = []
    for r in results:
        search_snippets[int(r['id'])] = hl[r['id']]
        pk_list.append(r['id'])
    results = query.filter(pk__in=pk_list)
    return {'results':results, 'search_snippets': search_snippets}

def apply_filter(query_filters, q=Resource.objects.all(), per_page_limit=config.per_page_limit):
    v = {}
    for filter in query_filters:
        filter_value = query_filters[filter]
        if filter[-3:] == 'tag':
            mm_rec = models.Tag.objects.filter(name__in=filter_value)
            q = q.filter(tags__in=mm_rec)
        # elif filter[-4:] == "term":
        #     text_search_results = text_search(filter_value, q)
        #     v.update(text_search_results['search_snippets']
        #     q = text_search_results['results']

        elif filter[-6:] == 'report':
            mm_rec = models.Report.objects.filter(name__in=filter_value)
            q = q.filter(reports__in=mm_rec)
            if filter_value == ['Weekly Reads']:
                v['nav'] = 'weekly_reads'
        elif filter[-6:] == 'office':
            mm_rec = models.Office.objects.filter(name__in=filter_value)
            mm_rec = models.Feed.objects.filter(offices__in=mm_rec)
            q = q.filter(feeds__in=mm_rec)
            if filter_value == ['SSG']:
                v['nav'] = 'SSG'

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
    return v

def MainPage(request, template=""):
    v = {}
    v['nav'] = 'home'
    filters = dict(request.GET.lists())
    v.update(apply_filter(filters))
    next_perams = request.GET.urlencode()
    next_perams = re.sub('[&s,s]=[0-9]{,5}', "", next_perams)
    next_perams += "&s=" + str(v.get('next_offset', '0'))
    v['show_more_url'] = '/q/ajax/?' + next_perams
    
    if template == "ajax":
        template_file = '/main/list_view.html'
    else:
        template_file = '/main/home.html'

    return HttpResponse(render.load(template_file, v))



# def read(request):
#     if request.method == "GET":
#         rec_key = request.GET.dict()['k']
#         rec = Resource.objects.get(pk=rec_key)
#         template_file = '/main/read.html'
#         md = markdown.Markdown()
#         if rec.content not in [None, ""]:
#             rec.content_html = md.convert(rec.content)
#         else:
#             rec.content_html = "<p>I'm sorry the content you are looking for was not able to be caputured</p>"
#         v = {'rec': rec}
#         return HttpResponse(render.load(template_file, v))
