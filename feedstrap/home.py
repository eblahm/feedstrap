from filter import apply_filter, generate_filter_tags
import render
from models import StaticPage as StaticPageModel


def MainPage(request, template=""):
    v = {}

    # Identify newcomers and give them some welcome content
    filter_conditions = request.GET.dict()
    v['auth'] = request.user.is_authenticated()
    if len(filter_conditions) == 0 and v['auth'] == False:
        alert_query = StaticPageModel.objects.filter(slug='welcome')
        if alert_query.count() > 0:
            v['alert'] = alert_query.get().content

    # load all the data pertaining to database queries
    v.update(apply_filter(request))

    # make sure the templates are aware of get perameters
    v.update(filter_conditions)

    # has the user landed at the page or just clicked "Show More"?
    if template == "ajax":
        template_file = '/main/list_view.html'
    else:
        template_file = '/main/home.html'
        v['get_query'] = request.GET.urlencode()
        v['filter_tags'] = generate_filter_tags(request)

    return render.response(request, template_file, v)


def StaticPage(request, static_page=""):
    v = {}
    q = StaticPageModel.objects.filter(slug=static_page)
    if q.count() == 1:
        v['static_page'] = q.get()
        v['nav'] = v['static_page'].slug
        template_file = '/main/static.html'
    else:
        template_file = '/main/404.html'
    return render.response(request, template_file, v)
