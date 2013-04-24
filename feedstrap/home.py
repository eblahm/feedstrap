from django.http import HttpResponse
from filter import apply_filter, generate_filter_tags
import render


def MainPage(request, template=""):
    v = {}
    v['nav'] = 'home'
    v.update(apply_filter(request))
    v.update(request.GET.dict())
    if template == "ajax":
        template_file = '/main/list_view.html'
    else:
        template_file = '/main/home.html'
        v['get_query'] = request.GET.urlencode()
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