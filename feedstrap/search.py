import operator

from django.db.models import Q

from models import Resource
from filter import Filter, advanced_filters


class OR_Statement(Filter):
    # for display purposes only
    name = "OR"
    color = "black"

class AdvancedSearch():
    def __init__(self):
        # pending "OR" statments between query expressions
        # subsets must be generated, then "OR"-ed together
        self._pending_queries = [ [] ] # only one level of subset is allowed

        # multiple conditions are restrictive and continually limiting by default, unless specified with "OR"
        self._and_statement = True
        self.registered_filters = {}
        for f in advanced_filters:
            self.registered_filters[f.name] = f
        self._base_model = Resource
        self.applied_filters = []

    def _apply(self, name, condition):
        if condition == 'OR' and name == "andor":
            # or statments are passed like conditions and provide information about what to do with the next condition
            # in this event modify _and_statment so the next condition passed to apply() will be included in a new subset
            self._and_statement = False
            filter = OR_Statement()
            return filter

        filter = self.registered_filters.get(name, False)
        if filter: 
            filter = filter()
            exp = filter.query_expression
            formated_condition = filter.process_string_input(condition)
            
            q = Q((exp, formated_condition))
    
            # django Q() allows for &,|
            if not self._and_statement:
                # create a new subset using this query as first item
                # any subsequent queryies will be treated as a part of this subset until "OR" appears again
                self._pending_queries.append([])
                self._and_statement = True

            # append this query to the most recent subset
            self._pending_queries[-1].append(q)

            return filter

    def get_results(self, get_parameters):

        # apply all the filters, in order
        # get perams should look like {"1_tags": "Health Care", "2_reports": "weekly reads"}
        sorted_params = sorted(get_parameters.iteritems(), key=operator.itemgetter(0)) 
        for condition_name, condition in sorted_params:
            filter_name = condition_name.split("_")[-1] # ex. 1_tags >> tags
            
            filter = self._apply(filter_name, condition)
            if filter:
                # add some meta data and add filter to applied list

                inverse_get = get_parameters.copy()
                del inverse_get[condition_name]
                filter.inverse = inverse_get.urlencode() # the inverse get parameters allow for the X click

                filter.display_value = filter._get_display_value(condition)

                self.applied_filters.append(filter)

        # construct query object using query expressions in each subset
        processed_subsets = []
        for subset in self._pending_queries:
            if len(subset) > 0:
                # use first item in list as the base for other queries
                # if more than one query
                # they each should be "AND"-ed together
                base = subset[0]
                for q in subset[1:]:
                    base = base & q
                processed_subsets.append(base)
                    
        if len(processed_subsets) == 0:
            # invalid query expressions
            return self._base_model.objects.all().order_by('-date')
        elif len(processed_subsets) == 1:
            # no "OR" statments found, only one subset available
            return self._base_model.objects.filter(processed_subsets[0]).order_by('-date')
        else:
            # subsets should be "OR" ed together
            q = processed_subsets[0]
            for ps in processed_subsets[1:]:
                q = q | ps
            return self._base_model.objects.filter(q).distinct().order_by('-date')

