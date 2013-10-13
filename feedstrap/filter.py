from datetime import datetime
import json

from django.http import HttpResponse
from django import forms
from django.contrib.auth.models import User

from models import *


class Filter():
    form_element = forms.CharField()
    name = ''
    color = 'black'

    condition_model = Resource
    query_expression = ''
    pk_search = False
    display_value = ""
    in_form_name = ""
    after_or = False
    inverse = ""
    value = ""
    count = 1

    def __init__(self):
        self.in_form_name = str(self.count) + "_" + self.name

    def _pk_to_name(self, condition_model, pk):
        """
        as an alternative to the standard display_value method
        and in order to make it more clear for the user of advanced search widget
        return name of underlying item assoicated with the selected pk
        """

        q_by_pk = condition_model.objects.filter(pk=pk)
        if q_by_pk:
            return q_by_pk.get().name
        else:
            return ''

    def _get_display_value(self, queried_value):
        """
        return a string representing search condition
        """

        if self.pk_search:
            return self._pk_to_name(self.condition_model, queried_value)
        else:
            return queried_value


    def process_string_input(self, sinput):
        if isinstance(sinput, unicode):
            return sinput.encode('utf-8')
        else:
            return str(sinput)

    def render_widget(self):
        self.form_element.attrs.update({'class': "primary_filter"})
        return self.form_element.render(self.in_form_name, self.value)

class TagsFilter(Filter):
    name = 'tags'
    color = '#0088CC'
    query_expression = 'tags__name'
    condition_model = Tag
    form_element = forms.TextInput(attrs={'data-ui': 'tags_autocomplete'})

class TextFilter(Filter):
    name = 'term'
    color = '#0088CC'

class MustacheDefault(TagsFilter):
    count = '{{filter_count}}'
    def render_widget(self):
        self.form_element.attrs.update({'class': "{{c}}"})
        return self.form_element.render(self.in_form_name, self.value)

class PersonFilter(Filter):
    name = 'person'
    color = 'orange'
    query_expression = 'feeds__user__first_name'
    condition_model = Feed
    form_element = forms.Select(choices=generate_choices(User, 'first_name', 'first_name'))

class FeedsFilter(Filter):
    name = 'feeds'
    color = 'orange'
    query_expression = 'feeds__pk'
    condition_model = Feed
    pk_search = True
    form_element = forms.Select(choices=generate_choices(Feed))

class ESILFilter(Filter):
    name = 'esil'
    color = 'red'
    query_expression = 'topics__pk'
    condition_model = Topic
    pk_search = True
    form_element = forms.Select(choices=generate_choices(Topic))

class ReportFilter(Filter):
    name = 'report'
    color = '#2D6987'
    query_expression = 'reports__name'
    condition_model = Report
    form_element = forms.Select(choices=generate_choices(Report, 'name', 'name'))

class DateToFilter(Filter):
    name = 'date to'
    color = 'purple'
    query_expression = 'date__lte'
    form_element = forms.TextInput(attrs={'data-ui': 'datepicker'})
    def process_string_input(self, sinput):
        return datetime.strptime(sinput, '%Y-%m-%d')


class DateFromFilter(DateToFilter):
    name = 'date from'
    query_expression = 'date__gte'

class OfficeFilter(Filter):
    name = 'office'
    color = 'green'
    query_expression = 'offices__name'
    condition_model = Office
    form_element = forms.Select(choices=generate_choices(Office,'name', 'name'), )

advanced_filters = [TagsFilter, PersonFilter, FeedsFilter, ESILFilter, ReportFilter, DateToFilter, DateFromFilter, OfficeFilter]

def advanced_form():
    all_elements = []
    for af in advanced_filters:
        af = af()
        af.form_element.attrs.update({'class': ""})
        all_elements.append(af.form_element.render(af.name, None))
    return "".join(all_elements)



def get_tags():
    tag_cache = cache.get('all_tags')
    if tag_cache == None:
        all_tags = sorted([t.name for t in Tag.objects.all()])
        cache.set('all_tags', all_tags)
    else:
        all_tags = tag_cache
    return all_tags

def data(request, model=None):
    response = HttpResponse(content_type='application/json')
    dtypes = {
        'tags': get_tags(),
        'offices': [o.name for o in Office.objects.all()]
    }
    response.write(json.dumps(dtypes.get(model, ['error'])))
    return response
