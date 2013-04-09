import os
import jinja2

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def load(template_file, template_values={}):
    template = jinja_environment.get_template(template_file)
    return template.render(template_values)