import render
from models import StaticPage as StaticPageModel
from search import AdvancedSearch, full_text_search
from config import per_page_limit
from filter import TextFilter


def MainPage(request, template=""):
    """
    the main http request handler for feedstrap
    traffic for common database queries go through this handler
    """

    v = {} # template values
    # Identify newcomers and give them some welcome content
    if len(request.GET) == 0 and not request.user.is_authenticated():
        alert = StaticPageModel.objects.filter(slug='welcome')
        if alert:
            v['alert'] = alert.get().content

    # load info pertaining to database queries
    v['search'] = AdvancedSearch()
    if request.GET.get('term', False):
        # full text search terms look like regular db queries to the user but are actually handled by solr
        # and involve entirely different search modules
        text_filter = TextFilter()
        text_filter.display_value = request.GET['term']
        v['full_text_search'] = True
        v['search'].applied_filters = [text_filter]
        v['results'], v['total'] = full_text_search(request.GET['term'])
        real_total = len(v['results'])
    else:
        v['results'] = v['search'].get_results(request.GET)
        v['total'] = v['results'].count()
        real_total = v['total']

    # where are we in terms of offset?
    try: start_offset = int(request.GET.get('s', 0))
    except: start_offset = 0
        
    # fetch db data according to offset and per page limit
    limit = start_offset + per_page_limit
    v['results'] = v['results'][start_offset:limit]
    
    # only allow for "show more" if there are actually more to show
    if real_total >= (limit + 1):
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

