from jinja2 import Environment, PackageLoader
from feedstrap.models import Report, Tag
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
    template_values.update(v)
    template = env.get_template(template_file)
    return template.render(template_values)
