from django.http import HttpResponse
from filter import apply_filter, generate_filter_tags
import render
from models import StaticPage as StaticPageModel

def MainPage(request, template=""):
    filter_conditions = request.GET.dict()
    v = {}
    v['admin'] = request.user.is_authenticated()
    v['peram_count'] = len(filter_conditions)
    if v['peram_count'] == 0 and v['admin'] == False: 
        v['alert'] = True
    v.update(apply_filter(request))
    v.update(filter_conditions)
    if template == "ajax":
        template_file = '/main/list_view.html'
    else:
        template_file = '/main/home.html'
        perams = request.GET.urlencode()
        v['get_query'] = perams
        v['filter_tags'] = generate_filter_tags(request)
    return HttpResponse(render.load(template_file, v))


def StaticPage(request, static_page=""):
    v = {}
    q = StaticPageModel.objects.filter(slug=static_page)
    if q.count() == 1:
        v['static_page'] = q.get()
        template_file = '/main/static.html'
    else:
        template_file = '/main/404.html'
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
