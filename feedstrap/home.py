from django.http import HttpResponse
from models import Resource, ResourceForm
import models
from django.core.context_processors import csrf
import render
import pytz
import json
from datetime import datetime


def dbedit(request):
    if request.method == "GET":
        rec_key = request.GET.dict()['k']
        rec = Resource.objects.get(pk=rec_key)
        template_file = '/main/form_db.html'
        v = {'rec': rec}
        v.update(csrf(request))
        v['resource_form'] = ResourceForm(instance=rec)
        return HttpResponse(render.load(template_file, v))
    elif request.method == "POST":
        pdic = request.POST.dict()
        rec = Resource.objects.get(pk=pdic['pk'])
        data_lists = dict(request.POST.lists())
        for i in data_lists:
            if i in ['pk', 'csrf_token'] or data_lists[i] == [""]:
                continue
            if len(data_lists[i]) == 1 and i <> 'tags':
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


def MainPage(request):
    v = {}
    v['nav'] = 'home'
    template_file = '/main/home.html'
    v['results'] = Resource.objects.all().order_by('-date')
    return HttpResponse(render.load(template_file, v))
