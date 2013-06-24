from jinja2 import Environment, PackageLoader
from django.http import HttpResponse
from django.core.cache import cache

from ssg_site.config import solr_enabled
from feedstrap.models import SidebarLink, StaticPage


env = Environment(loader=PackageLoader('feedstrap', 'templates'))


def response(request, template_file, template_values={}):
    v = {}
    v['auth'] = request.user.is_authenticated()
    if v['auth']:
        v['user'] = request.user

    # load the link items under the "Feed" section on the sidebar
    # this info is cached
    feed_navs = cache.get('feed_navs')
    if feed_navs == None:
        feed_navs = []
        for n in SidebarLink.objects.all().order_by("position"):
            feed_navs.append((n.parameters, n.name))
        cache.set('feed_navs', feed_navs)
    v['feed_navs'] = feed_navs

    # a dictionary to enable the "active" class links within the sidebar navigation
    feed_nav_lookup = dict(feed_navs)

    # if the user has searched sidebar nav link automatically
    # defaults to advanced search in the active state
    # unless the search is is a recognized "feed"
    perams = template_values.get('get_query', "")
    v['advanced_search'] = feed_nav_lookup.get(perams, True)

    # allows default advanced search nav link to be overriden within the views
    if template_values.get('nav', "") != '':
        template_values['advanced_search'] = False

    # determines weather or not to have a search bar on the top navbar
    v['solr_enabled'] = solr_enabled

    # static pages represent the links on the top navbar, linking to static-ish html pages
    static_pages = cache.get('static_pages')
    if static_pages == None:
        static_pages = [sp for sp in StaticPage.objects.filter(published=True).order_by('position')]
        cache.set('static_pages', static_pages)
    v['static_pages'] = static_pages

    # view template is updated based on the global data above
    template_values.update(v)

    # why do I use jinja2 instead of django templates, you ask... no good reason, just a bad habit
    template = env.get_template(template_file)
    return HttpResponse(template.render(template_values))
