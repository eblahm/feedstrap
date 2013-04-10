from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('feedstrap', 'templates'))

def load(template_file, template_values={}):
    template = env.get_template(template_file)
    return template.render(template_values)