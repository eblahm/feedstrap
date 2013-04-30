from jinja2 import Environment, PackageLoader
from feedstrap.models import Report, Tag

env = Environment(loader=PackageLoader('feedstrap', 'templates'))

def load(template_file, template_values={}):
    v = {'all_tags': sorted([t for t in Tag.objects.all()])}
    template_values.update(v)
    template = env.get_template(template_file)
    return template.render(template_values)