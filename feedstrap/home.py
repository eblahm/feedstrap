from django.http import HttpResponse
from models import Resource
import render

def dbedit(request):
    rec_key = request.GET.dict()['k']
    rec = Resource.objects.get(pk=rec_key)
    template_file = '/main/form_db.html'
    v = {'rec':rec}
    return HttpResponse(render.load(template_file, v))

def MainPage(request):
    v = {}
    v['nav'] = 'home'
    template_file = '/main/home.html'
    v['results'] = Resource.objects.all().order_by('-date')
    return HttpResponse(render.load(template_file, v))