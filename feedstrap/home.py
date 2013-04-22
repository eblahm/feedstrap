from django.http import HttpResponse
from models import Resource, ResourceForm, Topic
import models
from django.core.context_processors import csrf
import render
import pytz
import json
from datetime import datetime
from ssg_site import pysolr  # , markdown


def apply_filter(query_filters):


    q = Resource.objects.all()
    per_page_limit = 10
    v = {}
    for filter in query_filters:
        filter_value = query_filters[filter]
        if filter[-3:] == 'tag':
            mm_rec = models.Tag.objects.filter(name__in=filter_value)
            q = q.filter(tags__in=mm_rec)
        elif filter[-4:] == "term":
            solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
            results = solr.search(" ".join(filter_value), **{'hl': 'true',
                                                'hl.fl': '*',
                                                'hl.fragsize': 200,
                                                'hl.snippets': 3})
            v['search_snippets'] = {}
            hl = results.highlighting
            pk_list = []
            for r in results:
                v['search_snippets'][int(r['id'])] = hl[r['id']]
                pk_list.append(r['id'])
            q = q.filter(pk__in=pk_list)
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
        q = q[:per_page_limit]
    else:
        q = q[start_offset:start_offset + per_page_limit]

    if q.count() == per_page_limit:
        v['next_offset'] = start_offset + per_page_limit
    v['results'] = q
    return v



def dbedit(request):
    if request.method == "GET":
        rec_key = request.GET.dict()['k']
        rec = Resource.objects.get(pk=rec_key)
        rec.all_reports = [r.pk for r in rec.reports.all()]
        template_file = '/main/forms/basic.html'
        v = {'rec': rec}
        v.update(csrf(request))
        v['resource_form'] = ResourceForm(instance=rec)
        v['topics'] = Topic.objects.all()
        return HttpResponse(render.load(template_file, v))
    elif request.method == "POST":
        response_data = {}
        if not request.user.is_authenticated():
            response_data['save_status'] = 'You are not authorized to edit this record. If this is a mistake, <a href="/admin">please login</a>'
            json_response = json.dumps(response_data)
            return HttpResponse(json_response)
        else:
            pdic = request.POST.dict()
            rec = Resource.objects.get(pk=pdic['pk'])
            data_lists = dict(request.POST.lists())
            wr_response = data_lists.get('weekly_reads',"")
            wrr = models.Report.objects.get(name="Weekly Reads")
            if wr_response == ["on"]:
                rec.reports.add(wrr)
            else:
                rec.reports.remove(wrr)
            for i in data_lists:
                if i in ['pk', 'csrf_token', 'weekly_reads']:
                    continue
                elif i in ['reports', 'topics']:
                    mmField = getattr(rec, i)
                    for mm in mmField.all():
                        mmField.remove(mm)
                    for manytomany_pk in data_lists[i]:
                        mmRec = getattr(models, i.title()[:-1]).objects.get(pk=int(manytomany_pk))
                        mmField.add(mmRec)
                elif len(data_lists[i]) == 1 and i != 'tags':
                    setattr(rec, i, data_lists[i][0])
                elif i == 'tags':
                    tag_inputs = [t.strip() for t in data_lists[i][0].split(',')]
                    for tag in rec.tags.all():
                        if tag.name not in tag_inputs:
                            rec.tags.remove(tag)
                    for tag in tag_inputs:
                        try:
                            tag_rec = models.Tag.objects.get(name=tag)
                        except:
                            tag_rec = models.Tag.objects.create(name=tag)
                        rec.tags.add(tag_rec)

            rec.save()
            now_est = datetime.now().replace(tzinfo=pytz.timezone('America/New_York'))
            message = '<em>updated %s</em>' % (now_est.strftime('%I:%M:%S%p'))
            message = message.lower() + " EST"
            response_data['id'] = 'ar_%s' % (rec.pk)
            response_data['ajax_html'] = render.load('/main/list_view_article.html', {'i': rec})
            response_data['save_status'] = message
            json_response = json.dumps(response_data)
            return HttpResponse(json_response)



def MainPage(request, template=""):
    v = {}
    v['nav'] = 'home'
    query_filters = dict(request.GET.lists())
    v.update(apply_filter(query_filters))
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
