from datetime import datetime
import operator

from django.contrib.auth.models import User
from django import forms
from django.db.models import Q

from models import *
import models


class Filter():
    form_element = forms.CharField()
    name = ''
    color = 'black'
    
    condition_model = Resource
    query_expression = ''
    pk_search = False
    display_value = None
    inverse = ""

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
    form_element = forms.ChoiceField(choices=generate_choices(User, 'first_name', 'first_name'))

class FeedsFilter(Filter):
    name = 'feeds'
    color = 'orange'
    query_expression = 'feeds__pk'
    condition_model = Feed
    pk_search = True
    form_element = forms.ChoiceField(choices=generate_choices(Feed))

class ESILFilter(Filter):
    name = 'ESIL'
    color = 'red'
    query_expression = 'topics__pk'
    condition_model = Topic
    pk_search = True
    form_element = forms.ChoiceField(choices=generate_choices(Topic))

class ReportFilter(Filter):
    name = 'report'
    color = '#2D6987'
    query_expression = 'reports__name'
    condition_model = Report
    form_element = forms.ChoiceField(choices=generate_choices(Report, 'name', 'name'))

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
    form_element = forms.ChoiceField(choices=generate_choices(Office,'name', 'name'))


registered = [TagsFilter, PersonFilter, FeedsFilter, ESILFilter,
                     ReportFilter, DateToFilter, DateFromFilter, OfficeFilter]

class OR_Statement(Filter):
    # for display purposes only
    name = "OR"
    color = "black"

class AdvancedSearch():
    def __init__(self, registered=registered):
        # pending "OR" statments between query expressions
        # subsets must be generated, then "OR"-ed together
        self._pending_queries = [ [] ] # only one level of subset is allowed

        # multiple conditions are restrictive and continually limiting by default, unless specified with "OR"
        self._and_statement = True
        self.registered_filters = {}
        for f in registered:
            self.registered_filters[f.name] = f
        
        self._base_query = Resource.objects.all()
        self.applied_filters = []

    def _apply(self, name, condition, inverse_paramters):
        if condition == 'OR' and name == "ANDOR":
            # or statments are passed like conditions and provide information about what to do with the next condition
            # in this event modify _and_statment so the next condition passed to apply() will be included in a new subset
            self._and_statement = False
            thisOR = OR_Statement()
            thisOR.inverse_get_parameters = inverse_paramters
            self.applied_filters.append(thisOR)
            return None

        filter = self.registered_filters.get(name, False)
        if filter: 
            filter = filter()
            exp = filter.query_expression
            formated_condition = filter.process_string_input(condition)
            
            q = Q((exp, formated_condition))
    
            # django Q() allows for &,|
            if self._and_statement:
                # append this query to the most recent subset
                self._pending_queries[-1].append(q)
            else:
                # create a new subset using this query as first item
                self._pending_queries.append([q])
                # any subsequent queryies will be treated as a part of this subset until "OR" appears again
                self._and_statement = True
                
            filter.display_value = filter._get_display_value(condition)
            filter.inverse = inverse_paramters
            self.applied_filters.append(filter)
            return None

    def get_results(self, get_parameters):

        # apply all the filters, in order
        # get perams should look like {"1_tags": "Health Care", "2_reports": "weekly reads"}
        sorted_params = sorted(get_parameters.iteritems(), key=operator.itemgetter(0)) 
        for condition_name, condition in sorted_params:
            filter_name = condition_name.split("_")[-1] # ex. 1_tags >> tags
            
            # the inverse get parameters allow for the X click on each filter tag
            inverse_get = get_parameters.copy()
            del inverse_get[condition_name]
            self._apply(filter_name, condition, inverse_get.urlencode())

        # actually construct query object using query expressions in the subset
        processed_subsets = []
        for subset in self._pending_queries:
            if len(subset) > 0:
                # use first item in list as the base for other queries
                base = Resource.objects.all().filter(subset[0])
                # if more than one query
                # they each should be "AND"-ed together
                for q in subset[1:]:
                    base &= base.filter(q)
                processed_subsets.append(base)
                    
        if len(processed_subsets) == 0:
            # no valid query expressions
            return self._base_query.order_by('-date')
        elif len(processed_subsets) == 1:
            # no "OR" statments found, only one subset available
            return processed_subsets[0].order_by('-date')
        else:
            # subsets should be "OR" ed together
            results = []
            for ps in processed_subsets:
                results | ps
            return results.distinct().order_by('-date')
