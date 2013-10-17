from datetime import datetime
import operator
import urllib

from django.http import HttpResponseNotFound
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.core.cache import cache

from feedstrap import config
from feedstrap.filter import advanced_form, advanced_filters, MustacheDefault, TagsFilter
from feedstrap.models import SidebarLink, StaticPage, PostIt


def fixed_template_values():
    template_values = {}
    template_values['feed_navs'] = [f for f in SidebarLink.objects.filter(for_all_users=True)]
    # static pages represent the links on the top navbar, linking to static-ish html pages
    template_values['static_pages'] = StaticPage.objects.filter(published=True).order_by('position')
    # to show or not to show searchbox
    template_values['solr_enabled'] = config.solr_enabled
    # tell the view how to render the advanedd filter widget
    template_values['advanced_form'] = advanced_form()
    template_values['advanced_filters'] = advanced_filters
    # load template inside the template for dynamic client side rendering of additional filter widgets
    template_values['mustache_filter'] = [MustacheDefault()]
    template_values['default_filter'] = [TagsFilter()]
    cache.set('fixed_template_values', template_values)
    return template_values


def encode_params(get_request):
    """
    an alternative to HttpRequest.GET.urlencode()
    with better mirroring to the way the browser encodes forms
    also the params are ordered
    """

    def js_en(s):
        return urllib.quote(s, safe='~()*!.\'') # get the uri encoding to mirror javascript encoding

    conditions = []
    for condition, value in sorted(get_request.iteritems(), key=operator.itemgetter(0)):
        conditions.append(js_en(condition) + "=" + js_en(value))

    return "&".join(conditions)

def response(request, template_file, template_values={}):
    template_values.update(
        cache.get('fixed_template_values') or fixed_template_values()
    )

    template_values['auth'] = request.user.is_authenticated()
    template_values['user'] = request.user
    template_values['staff'] = request.user.is_staff

    template_values['get_query'] = encode_params(request.REQUEST)

    try:
        usr_ext = PostIt.objects.get(user=request.user)
        template_values['user_feed_navs'] = [f for f in usr_ext.sidebar_links.all()]
    except:
        template_values['user_feed_navs'] = []

    # which link should be highlighted?
    # the active sidebar link is by default "advanced search"
    template_values['advanced_search'] = True
    # unless ...
    # 1. the search recongized ie hyperlinked in the sidebar
    # 2. 'nav' is defined explicitly in the view

    all_navs = [f.parameters for f in template_values['user_feed_navs'] + template_values['feed_navs']]
    is_recognized = template_values['get_query'] in all_navs
    is_nav_overriden = template_values.get('nav', False)
    if is_recognized or is_nav_overriden:
        template_values['advanced_search'] = False


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