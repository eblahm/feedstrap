from datetime import datetime
import operator

from django.contrib.auth.models import User
from django import forms
from django.db.models import Q

from models import Resource, Tag, Report, Office, Feed, Topic


class Filter():
    def __init__(self):
        self._target_model = Resource
        self.pk_search = False
        self.name = ''
        self.color = 'black'
        self.condition_model = Resource
        self.query_expression = ''
        self.form_element = forms.CharField()
        self.inverse = ""

    def _pk_to_name(model, pk):
        """
        as an alternative to the standard display_value method
        and in order to make it more clear for the user of advanced search widget
        return name of underlying item assoicated with the selected pk
        """
        q_by_pk = model.objects.filter(pk=pk)
        if q_by_pk:
            return q_by_pk.get().name
        else:
            return ''

    def process_string_input(self, sinput):
        if isinstance(sinput, unicode):
            return sinput.encode('utf-8')
        else:
            return str(sinput)

    def display_value(self, queried_value):
        """
        return a string representing search condition
        """
        if self.pk_search:
            return self._pk_to_name(self.condition_model, queried_value)
        else:
            return queried_value


class OR_Statement(Filter):
    # for display purposes only
    name = "OR"
    color = "black"

class AdvancedSearch():
    def __init__(self, query):
        # pending "OR" statments between query expressions
        # subsets must be generated, then "OR"-ed together
        self._pending_queries = [ [] ] # only one level of subset is allowed

        # multiple conditions are restrictive and continually limiting by default, unless specified with "OR"
        self._and_statement = True
        self.registered_filters = {}

        self.query = query
        self.applied_filters = []

    def register_filters(self, filters):
        for f in filters:
            self.registered_filters[f.name] = f

    def _apply(self, name, condition, inverse_paramters):
        if condition == 'OR' and name == "ANDOR":
            # or statments are passed like conditions and provide information about what to do with the next condition
            # in this event modify _and_statment so the next condition passed to apply() will be included in a new subset
            self._and_statement = False
            thisOR = OR_Statement()
            thisOR.inverse_get_parameters = inverse_paramters
            self.applied_filters.append(thisOR)
            return self

        filter = self.registered_filters.get(name, None)
        if not filter:
            return self
            
        filter = filter()
        q = Q(filter.query_expression, filter.process_string_input(condition))

        # django Q() allows for &,|
        if self._and_statement:
            # append this query to the most recent subset
            self._pending_queries[-1].append(q)
        else:
            # create a new subset using this query as first item
            self._pending_queries.append([q])
            # any subsequent queryies will be treated as a part of this subset until "OR" appears again
            self._and_statement = True
        filter.inverse = inverse_paramters
        self.applied_filters.append(filter)
        return self

    def get_results(self, get_parameters):

        # apply all the filters, in order
        # get perams should look like {"1_tags": "Health Care", "2_reports": "weekly reads"}
        sorted_params = sorted(get_parameters.iteritems(), key=operator.itemgetter(0)) 
        for sp in sorted_params:
            name = sp.split("_")[-1] # ex. 1_tags >> tags
            condition = sorted_params[sp] # ex. Health Care
            
            # the inverse get parameters allow for the X click on each filter tag
            inverse_get = get_parameters.copy()
            del inverse_get[sp]
            self._apply(name, condition, inverse_get.urlencode())

        # either "OR" them or "AND" them together
        processed_subsets = []
        for subset in self._pending_queries:
            # actually fetch search results for each query expression in the subset
            # use first item in list as the base for other queries
            ps = [self._target_model.objects.filter(subset[0])]
            # if more than one query
            # they each should be "AND"-ed together
            for q in subset[1:]:
                ps[0] = ps[0] & self._target_model.objects.filter(q) 
                
            processed_subsets.append(ps)

        if len(processed_subsets) > 1:
            # subsets should be "OR" ed together
            results = []
            for ps in processed_subsets:
                results | ps
            return results.distinct().order_by('-date')
        else:
            # No "OR" statments were found
            return processed_subsets[0].order_by('-date')


    
class TagsFilter(Filter):
    name = 'tags'
    color = '#0088CC'
    query_expression = 'tags__name'
    condition_model = Tag
    form_element = forms.CharField(max_length=100)

class PersonFilter(Filter):
    name = 'person'
    color = 'orange'
    query_expression = 'feeds__user__first_name'
    condition_model = Feed
    form_element = forms.ChoiceField(choices=models.generate_choices(User, 'first_name', 'first_name'))

class FeedsFilter(Filter):
    name = 'feeds'
    color = 'orange'
    query_expression = 'feeds__pk'
    condition_model = Feed
    pk_search = True
    form_element = forms.ChoiceField(choices=models.generate_choices(models.Feed))

class ESILFilter(Filter):
    name = 'ESIL'
    color = 'red'
    query_expression = 'topics__pk'
    condition_model = Topic
    pk_search = True
    form_element = forms.ChoiceField(choices=models.generate_choices(models.Topic))

class ReportFilter(Filter):
    name = 'Report'
    color = '#2D6987'
    query_expression = 'reports__name'
    condition_model = Report
    form_element = forms.ChoiceField(choices=models.generate_choices(models.Report, 'name', 'name'))

class DateToFilter(Filter):
    name = 'Date To'
    color = 'purple'
    query_expression = 'date__lte'
    form_element = forms.DateField('%Y-%m-%d')
    def process_string_input(self, sinput):
        return datetime.strptime(sinput, '%Y-%m-%d')

class DateFromFilter(DateToFilter):
    name = 'Date From'
    query_expression = 'date__gte'

class OfficeFilter(Filter):
    name = 'Office'
    color = 'green'
    query_expression = 'offices__name'
    condition_model = Office
    form_element = forms.ChoiceField(choices=models.generate_choices(models.Office,'name', 'name'))

AS = AdvancedSearch()
AS.register_filters([TagsFilter, PersonFilter, FeedsFilter, ESILFilter,
                     ReportFilter, DateToFilter, DateFromFilter, OfficeFilter])
