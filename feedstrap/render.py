from jinja2 import Environment, PackageLoader
from feedstrap.models import Report, Tag, SidebarLink
from django.core.cache import cache

env = Environment(loader=PackageLoader('feedstrap', 'templates'))

def load(template_file, template_values={}):
    tag_cache = cache.get('all_tags')
    if tag_cache == None:
        all_tags = sorted([t for t in Tag.objects.all()])
        cache.set('all_tags', all_tags)
    else:
        all_tags = tag_cache
    v = {'all_tags': all_tags}
    feed_navs = cache.get('feed_navs')
    if feed_navs == None:
        feed_navs = []
        for n in SidebarLink.objects.all().order_by("position"):
            feed_navs.append((n.parameters, n.name))
        cache.set('feed_navs', feed_navs)
    feed_nav_lookup = dict(feed_navs)
    perams = template_values.get('get_query', None)
    v['advanced_search'] = feed_nav_lookup.get(perams, True)
    v['feed_navs'] = feed_navs
    template_values.update(v)
    if template_values.get('nav', "") != '':
        template_values['advanced_search'] = False
    template = env.get_template(template_file)
    return template.render(template_values)
