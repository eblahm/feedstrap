import pytz
import json
from datetime import datetime

from django.http import HttpResponse
from django.core.cache import cache
from django.core.context_processors import csrf

from models import Resource, ResourceForm, Topic, Tag
import models
import render

def get_tags():
    tag_cache = cache.get('all_tags')
    if tag_cache == None:
        all_tags = sorted([t for t in Tag.objects.all()])
        cache.set('all_tags', all_tags)
    else:
        all_tags = tag_cache
    return all_tags

def main(request):
    if request.method == "GET":
        v = {}
        v['all_tags'] = get_tags()
        rec_key = request.GET.dict()['k']
        rec = Resource.objects.get(pk=rec_key)
        rec.all_reports = [r.pk for r in rec.reports.all()]
        v['rec'] = rec
        v.update(csrf(request))
        v['resource_form'] = ResourceForm(instance=rec)
        v['topics'] = Topic.objects.all()
        template_file = '/main/forms/basic.html'
        return render.response(request, template_file, v)
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
                    if data_lists[i] == [""]:
                        data_lists[i] = []
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
                            rec.save()
                            if Resource.objects.filter(tags=tag).count() == 0:
                                tag.delete()
                        if tag.name == "":
                            rec.tags.remove(tag)
                    for tag in tag_inputs:
                        if tag != "":
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
            response_data['ajax_html'] = render.load('/main/list_view_article.html', {'i': rec, 'admin': True})
            response_data['save_status'] = message
            json_response = json.dumps(response_data)
            return HttpResponse(json_response)

def add_new(request):
    if request.method == "GET":
        v = {}
        v['all_tags'] = get_tags()
        g = request.GET
        rec = Resource(title=g['t'], link=g['l'], description=g['d'], date=datetime.now())
        v['rec'] = rec
        v.update(csrf(request))
        v['resource_form'] = ResourceForm(instance=rec)
        v['topics'] = Topic.objects.all()
        template_file = '/main/forms/post_it.html'
        return render.response(request, template_file, v)
    if request.method == "POST":
        v = {}
        template_file = '/main/forms/post_it.html'
        return render.response(request, template_file, v)

