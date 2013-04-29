from django.http import HttpResponse
from filter import apply_filter, generate_filter_tags
import render

feed_navs = {
    '': 'home',
    'offices=1': 'SSG',
    'reports=1': "weekly_reads",
}

def MainPage(request, template=""):
    v = {}
    v.update(apply_filter(request))
    v.update(request.GET.dict())
    if template == "ajax":
        template_file = '/main/list_view.html'
    else:
        template_file = '/main/home.html'
        perams = request.GET.urlencode()
        v['get_query'] = perams
        v['nav'] = feed_navs.get(perams, "")
        v['filter_tags'] = generate_filter_tags(request)
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
