import operator
import pysolr
import render

from django.db.models import Q
from django import forms

from models import Resource
from filter import Filter, advanced_filters



class OR_Statement(Filter):
    name = "OR"
    color = "black"
    def _get_display_value(self, queried): return None


def widget_maker(f):
    class af_widget(forms.Form):
        def __init__(self, *args, **kwargs):
            super(af_widget, self).__init__(args, kwargs)
            self.fields[f.name] = f.form_element
    return af_widget()

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

    def _construct_Q(self, name, condition):
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
        """
        the primary method for returning search results
        the get_get_parameters argument consists of conditions constructed by the javascript advanced search widget
        get perams should look like {"1_tags": "Health Care", "2_reports": "weekly reads"}
        return queryset that corresponds to get params
        """

        sorted_params = sorted(get_parameters.iteritems(), key=operator.itemgetter(0))
        for condition_name, condition in sorted_params:
            filter_name = condition_name.split("_")[-1] # ex. 1_tags >> tags

            # construct Q() objects for each filters, in order
            filter = self._construct_Q(filter_name, condition)
            if filter:
                # also generate metadata for the view for each valid filter
                inverse_get = get_parameters.copy()
                del inverse_get[condition_name]
                filter.inverse = inverse_get.urlencode() # the inverse get parameters allow for the X click
                filter.display_value = filter._get_display_value(condition)
                filter.count = len(self.applied_filters) + 1
                filter.in_form_name = str(filter.count) + '_' + filter.name
                filter.value = condition
                if len(self.applied_filters) > 1 and self.applied_filters[-1].name == "OR":
                    filter.after_or = True
                self.applied_filters.append(filter)

        # construct queryset for each subset
        processed_subsets = []
        for subset in self._pending_queries:
            if len(subset) > 0:
                # use first item in list as the base for other queries
                # if more than one query
                # they each should be "AND"-ed together
                base = self._base_model.objects.all()
                for q in subset:
                    base = base.filter(q) # this may be a memory suck, unfortunatly I can't get the alternative ie .filter(*[Q(),Q()]) to be properly restrictive
                processed_subsets.append(base)

        if len(processed_subsets) == 0:
            # invalid query expressions or None found
            return self._base_model.objects.all().order_by('-date')
        elif len(processed_subsets) == 1:
            # no "OR" statments found, only one subset available
            return processed_subsets[0].order_by('-date')
        else:
            # subsets should be "OR" ed together
            q = processed_subsets[0]
            for ps in processed_subsets[1:]:
                q = q | ps
            return q.distinct().order_by('-date')



def normalize(x):
    try:
        return str(x)
    except:
        try:
            return x.decode('utf8').encode('ascii', 'xmlcharrefreplace')
        except:
            return x.encode('ascii', 'xmlcharrefreplace')

def remove_control_characters(s):
    return "".join(c for c in s if ord(c) >= 32)


def doc_maker(db_obj):
    if db_obj.content is not None and db_obj.content != "":
        db_obj.content = normalize(db_obj.content)
        db_obj.content = remove_control_characters(db_obj.content)
    tags_list = sorted([t.name for t in db_obj.tags.all()])
    db_obj.tags_cont = ", ".join(tags_list)
    template_values = {'r':db_obj}
    text = render.load('search/index.html', template_values)
    text = normalize(text)
    doc = {"id": str(db_obj.pk), "content": text, "url": db_obj.link}
    return doc

class solr_server():
    def __init__(self):
        self.solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)

    def reindex_all(self):
        current_docs = self.solr.search('*:*')
        deleted = 0
        for d in current_docs:
            self.solr.delete(id=d['id'])
            deleted += 1
        docs = []
        added = 0
        q = Resource.objects.all()
        for r in q:
            print added
            docs.append(doc_maker(r))
            added += 1
        self.solr.add(docs)
        return {'deleted': deleted, 'added': added}
    def add_resource(self, r):
        solr = self.solr
        doc = doc_maker(r)
        solr.add([doc])
        return doc

    def delete_resource(self, resource_item):
        self.solr.delete(id=resource_item.pk)
        return 'deleted'

def solr():
    return solr_server()

def full_text_search(term):
    solr = pysolr.Solr('http://localhost:8983/solr/', timeout=10)
    srt = 'score desc'
    solr_results = solr.search(term, **{'hl': 'true',
                                        'hl.fl': '*',
                                        'fl': '*,score',
                                        'rows': 50,
                                        'sort': srt,
                                        'hl.fragsize': 200,
                                        'hl.snippets': 3})
    # each solr result should correspond to sql db resource
    # must create custom made interable so search results comply with view settings
    # each sql db resource is given temporary highlighted keyword snippets attribute
    hl = solr_results.highlighting
    total = solr_results.hits
    results = []
    for textDocument in solr_results:
        dbResource = Resource.objects.filter(pk=int(textDocument['id']))
        if dbResource:
            snippets = []
            for snip in hl.get(textDocument['id']).get('content', []):
                snippets.append(snip)
            rec = dbResource.get()
            rec.snippets = "".join(snippets)
            results.append(rec)
    return (results, total)