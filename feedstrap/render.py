from datetime import datetime

from django.http import HttpResponseNotFound
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.core.cache import cache

from feedstrap import config
from feedstrap.filter import advanced_form, advanced_filters, MustacheDefault, TagsFilter
from feedstrap.models import SidebarLink, StaticPage


def enable_navigation(get_query="", active_nav=False):
    """
    Returns a dictionary with the necessary information to tell the view: 
    1. how to name and order the sidebar and topbar
    2. how to highlight navigation links as being active
    3. wheater or not to show a full text search box in the topbar
    """
    
    # cached list of ordered pairs representing links on the sidebar
    feed_navs = cache.get('feed_navs')
    if feed_navs == None:
        feed_navs = []
        for sidebarlink in SidebarLink.objects.all().order_by("position"):
            feed_navs.append((sidebarlink.parameters, sidebarlink.name))
        cache.set('feed_navs', feed_navs)
        
    # which link should be highlighted?
    # the active sidebar link is by default "advanced search"
    advanced_search = True
    # unless ...
    # 1. the search recongized ie hyperlinked in the sidebar 
    # 2. 'nav' is defined explicitly in the view
    is_recognized = dict(feed_navs).get(get_query, False)
    is_nav_overriden = active_nav
    if is_recognized or is_nav_overriden: 
        advanced_search = False
        
    # static pages represent the links on the top navbar, linking to static-ish html pages
    static_pages = cache.get('static_pages')
    if static_pages == None:
        static_pages = [sp for sp in StaticPage.objects.filter(published=True).order_by('position')]
        cache.set('static_pages', static_pages)
        
    # to show or not to show searchbox
    solr_enabled = config.solr_enabled
    
    return {
        'feed_navs': feed_navs,
        'advanced_search': advanced_search,
        'static_pages': static_pages,
        'solr_enabled': solr_enabled
        }
    

def response(request, template_file, template_values={}):

    # tell the view how to render the advanedd filter widget
    template_values['advanced_form'] = advanced_form()
    template_values['advanced_filters'] = advanced_filters

    # load template inside the template for dynamic client side rendering of additional filter widgets
    template_values['mustache_filter'] = [MustacheDefault()]
    template_values['default_filter'] = [TagsFilter()]

    template_values['auth'] = request.user.is_authenticated()
    template_values['user'] = request.user
    template_values['staff'] = request.user.is_staff
    
    template_values.update(enable_navigation(
        get_query = template_values.get('get_query', ''),
        active_nav = template_values.get('nav', False)
        ))

    return render_to_response(template_file,
                              template_values,
                              context_instance=RequestContext(request))


def load(template_file, template_values={}):
    return render_to_string(template_file, template_values)


def not_found(request):
    try:
        log_file = open('/var/www/media/feedstrap/404_log', 'a')
        error = "%s - %s - %s\n" % (datetime.now().strftime("%X %x"), request.META.get('REMOTE_ADDR', '?'), request.get_full_path())
        log_file.writelines(error)
        log_file.close()
    except:
        pass
    return HttpResponseNotFound(load('main/404.html'))