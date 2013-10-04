from filter import apply_filter, generate_filter_tags
import render
from models import StaticPage as StaticPageModel
from search import AdvancedSearch
from config import per_page_limit


def MainPage(request, template=""):
    v = {}

    # Identify newcomers and give them some welcome content
    filter_conditions = request.GET.dict()
    v['auth'] = request.user.is_authenticated()
    if len(filter_conditions) == 0 and v['auth'] == False:
        alert_query = StaticPageModel.objects.filter(slug='welcome')
        if alert_query.count() > 0:
            v['alert'] = alert_query.get().content

    # load info pertaining to database queries
    class pageinfo(AdvancedSearch): pass
    PG = pageinfo()
    v['results'] = PG.get_results(request.GET)
    v['total'] = len(v['results'])
    v['search'] = PG
    
     
    # where are we in terms of offset?
    try:
        start_offset = int(request.GET.get('s', 0))
    except:
        start_offset = 0
        
    # fetch db data according to offset and per page limit
    limit = start_offset + per_page_limit
    v['results'] = v['results'][start_offset:limit]
    
    # only allow for "show more" if there are actually more to show
    if v['total'] >= (limit + 1):
        get_request_copy = request.GET.copy()
        get_request_copy.__setitem__('s', limit)
        v['show_more_perams'] = get_request_copy.urlencode()
    elif v['total'] > 0:
        v['end_info'] = 'End of Search Results'
    else:
        v['end_info'] = 'No Results Found for that Search'

    # has the user landed at the page or just clicked "Show More"?
    if template == "ajax":
        template_file = 'main/list_view.html'
    else:
        template_file = 'main/home.html'
        v['get_query'] = request.GET.urlencode()

    return render.response(request, template_file, v)


def StaticPage(request, static_page=""):
    v = {}
    q = StaticPageModel.objects.filter(slug=static_page)
    if q.count() == 1:
        v['static_page'] = q.get()
        v['nav'] = v['static_page'].slug
        template_file = 'main/static.html'
        return render.response(request, template_file, v)
    else:
        return render.not_found(request)
