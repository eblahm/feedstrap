from django.http import HttpResponse
from models import Resource, ResourceForm
import models
from django.core.context_processors import csrf
import render
import pytz
import json
from datetime import datetime
from ssg_site import pysolr

def apply_filter(query_filter):
    q = Resource.objects.all()
    per_page_limit = 10
    new_template_values = {}
    tag_filter = query_filter.get('tag', "")
    report_filter = query_filter.get('report', "")
    term_filter = query_filter.get('term', "")
    if term_filter <> "":
        solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
        results = solr.search(term_filter, **{'hl': 'true','hl.fl': '*', 'hl.fragsize': 200, 'hl.snippets':3})
        new_template_values['search_snippets'] = {}
        new_template_values['term'] = term_filter
        hl = results.highlighting
        pk_list = []
        for r in results:
            new_template_values['search_snippets'][int(r['id'])] = hl[r['id']]
            pk_list.append(r['id'])
        q = q.filter(pk__in=pk_list)
    if tag_filter <> "":
        tag_rec = models.Tag.objects.get(name=query_filter['tag'])
        q = q.filter(tags=tag_rec)
        new_template_values['tag'] = tag_filter
    if report_filter <> "":
        report_rec = models.Report.objects.get(name=query_filter['report'])
        q = q.filter(reports=report_rec)
        new_template_values['report'] = report_filter
    if term_filter <> "":
        q = q.order_by('-date')

    start_offset = query_filter.get('s', '0')
    start_offset = int(start_offset)
    if start_offset == 0:
        q = q[:per_page_limit]
    else:
        q = q[start_offset:start_offset+per_page_limit]

    if q.count() == per_page_limit:
        new_template_values['next_offset'] = start_offset + per_page_limit

    new_template_values['results'] = q
    return new_template_values

def dbedit(request):
    if request.method == "GET":
        rec_key = request.GET.dict()['k']
        rec = Resource.objects.get(pk=rec_key)
        rec.all_reports = [r.pk for r in rec.reports.all()]
        template_file = '/main/form_db.html'
        v = {'rec': rec}
        v.update(csrf(request))
        v['resource_form'] = ResourceForm(instance=rec)
        return HttpResponse(render.load(template_file, v))
    elif request.method == "POST":
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
            # if i in ['reports', 'topics']:    
            #     mmField = getattr(rec, i)
            #     for mm in mmField.all():
            #         mmField.remove(mm)
            #     for manytomany_pk in data_lists[i]:
            #         mmRec = getattr(models, i.title()[:-1]).objects.get(pk=int(manytomany_pk))
            #         mmField.add(mmRec)            
            elif len(data_lists[i]) == 1 and i <> 'tags':
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

        response_data = {}
        response_data['id'] = 'ar_%s' % (rec.pk)
        response_data['ajax_html'] = render.load('/main/article_short.html', {'i': rec})
        response_data['save_status'] = message
        json_response = json.dumps(response_data)
        return HttpResponse(json_response)


def MainPage(request,  template=""):
    v = {}
    query_filter = request.GET.dict()
    v.update(apply_filter(query_filter))
    v['nav'] = 'home'
    if template == "ajax":
        template_file = '/main/list_view.html'
    else:
        template_file = '/main/home.html'

    return HttpResponse(render.load(template_file, v))