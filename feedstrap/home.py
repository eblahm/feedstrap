import fix_path
import webapp2
import models
import date_tools
import forms
import render
import search_tools as mst
from datetime import datetime
from google.appengine.ext import db
from google.appengine.api import memcache
import urllib
import urllib2
from google.appengine.api import search
from google.appengine.api import users
from xlwt import Worksheet, Workbook
from pytz.gae import pytz
import types

def get_view(handler):
        if handler.request.get('view') == "":
            return 'list'
        else:
            return handler.request.get('view')
            
def ude(raw): # for decoding encoded uri strings
  raw_encoded = urllib2.quote(unicode(raw).encode('utf8'))
  return urllib2.unquote(raw_encoded).decode('utf8')

def dstore_update(v):
    v['query_type'] = 'dstore'
    qstart = 'WHERE '
    order = ' ORDER BY date DESC'
    qsplit = v['query_string'].split(' OR ')
    if len(qsplit) == 1:
        v['query_string'] += order
        q = models.sources.gql(v['query_string'])
        if v['pre_curs'] <> "": 
            q = q.with_cursor(v['pre_curs'])
        v['result_count'] = q.count()
        v['results'] = q.fetch(10)
        if len(v['results']) == 10:
            if models.sources.gql(v['query_string']).with_cursor(q.cursor()).get() <> None:
                v['next_cursor'] = q.cursor()
    else:
        q = models.sources.gql(qsplit[0]).fetch(1000)
        for or_query in qsplit[1:]:
            q.extend(models.sources.gql(qstart + or_query).fetch(1000))
        v['results'] = sorted(q, key=lambda rec: rec.date, reverse=True)
        v['result_count'] = len(q)
    return v
                
def full_text_update(v):
    v['results'] = []

    if v['pre_curs'] == "":        
        q = mst.my_finder(v['term'])          
    else:
        q = mst.my_finder(v['term'], cursor=v['pre_curs'])
    v['result_count'] = str(q.number_found)
    for i in q:
        rec = db.get(i.doc_id)
        if rec <> None:
            v['results'].append(rec)
        else:
            search.Index(name="sources_docs").delete(i.doc_id)
    curs = q.cursor
    if curs <> None:
        v['next_cursor'] = curs.web_safe_string
    return v

def db_save(rec, v):
    for field in v:
        if v[field] == "":
            v[field] = None
        setattr(rec, field, v[field])

    rec.last_updated = datetime.now()    
    rec.put()
    return rec

class MainPage(webapp2.RequestHandler):
    def get(self):
        v = {}
        v['nav'] = 'home'
        v['view'] = get_view(self)
        v['query_type'] = self.request.get('qt')
        v['pre_curs'] = self.request.get('c')
        v['term'] = self.request.get('term')       
        if len(self.request.arguments()) == 0 or v['query_type'] == 'dstore':
            v['query_string'] = self.request.get('query_string')
            v = dstore_update(v)
        else:
            v = full_text_update(v)        

        if v['pre_curs'] == "":
            template_file = '/templates/main/home.html'
        elif v['view'] == 'list':
            template_file = '/templates/main/list_view.html'
        elif v['view'] == 'table':
            template_file = '/templates/main/table_view.html'
            v['standalone'] = True


        this_user = users.get_current_user()
        if this_user <> None:
            mem_code = this_user.user_id() + "_table_fields"
            v['default_fields'] = memcache.get(mem_code)
        else:
            v['default_fields'] = memcache.get("table_fields")

        if v['default_fields'] == None:
            v['default_fields'] = [('date','8.32%'), ('title','25%'), ('tags','16.64%'), ('description','25%'), ('relevance','25%')]
        
        v['default_checked'] = [c[0] for c in v['default_fields']]
        
        v['model_properties'] = sorted([p for p in models.sources.properties()])
        index = 0
        for df in v['default_fields']:
            v['model_properties'].remove(df[0])
            v['model_properties'].insert(index, df[0])
            index += 1
        
        processed_results = []
        for i in v['results']:
            new = {'key':str(i.key()), 'values':[]}
            for f in v['default_fields']:
                val = getattr(i, f[0])
                if type(val) == types.StringType:
                    pass
                elif val == None:
                    val = ""
                elif type(val) == types.ListType:
                    val = ", ".join(val)
                else:
                    try:
                        val = val.strftime('%d %b %y')
                    except:
                        pass
                this_tup = (f[0], val, f[1])
                new['values'].append(this_tup)
            processed_results.append(new)
        v['processed_results'] = processed_results
        
        self.response.out.write(render.load(template_file, v))

class db_edit_click(webapp2.RequestHandler):
  def get(self):
    item = db.get(self.request.get('k'))
    v = {'rec' : item}
    v['esil'] = forms.get_esil_topics()

    self.response.out.write(render.load('/templates/main/form_db.html', v))

class db_save_click(webapp2.RequestHandler):
  def post(self):
    list_properties = ['esil', 'capabilities', 'policy', 'tags']
    
    rec = db.get(self.request.get('db_key'))
    formated_dic = {}
    
    for i in self.request.POST.items():
        if i[0] == "db_key":
            continue
        try:
            formated_dic[i[0]] = formated_dic[i[0]] + "," + i[1]
        except:
            formated_dic[i[0]] = i[1]
    
    for i in list_properties:
        try:
            current_value = formated_dic[i]
        except:
            continue
        formated_dic[i] = sorted([t.strip() for t in str(current_value).split(',') if t <> ""])
        


    saved_record = db_save(rec, formated_dic)
    now_est = datetime.now().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('America/New_York'))
    message = '<em>updated %s</em>' % (now_est.strftime('%I:%M:%S%p'))
    message = message.lower() + " EST"
    self.response.out.write(message)


class AjaxHandler(webapp2.RequestHandler):
    def get(self, ajax_type):
        html = '--'
        if ajax_type == 'get_input':
            field_name = self.request.get('f')
            filter_count = self.request.get('filter_count')
            if filter_count <> "":
                field_name = filter_count + "___" + field_name
            html = forms.form_generate(field_name)
            self.response.out.write(html)
    def post(self):
        method = self.request.get("method")
        field_name = self.request.get("field")
        field_value = self.request.get(field_name)
        dbks = [k for k in self.request.get('dbks').split(",") if k <> ""]
        for k in dbks:
            rec = db.get(k)
            if method == 'overwrite':
                if type(getattr(rec, field_name)) == types.StringType or getattr(rec, field_name) == None:
                    setattr(rec, field_name, field_value)
                if type(getattr(rec, field_name)) == types.ListType:
                    setattr(rec, field_name, str(field_value).split(','))
                rec.put()
        self.response.out.write('good stuff!')
                
class NewFieldsHandler(webapp2.RequestHandler):
    def get(self):
        if self.request.get('with_ratios') == 'yes':
            cols = self.request.get_all('col')
            new_defaults = []
            for col in cols:
                c = col.split(',')
                ratio = str(float(c[1])*100)+"%"
                new_defaults.append((c[0],ratio))
        else:
            new_fields = [f for f in self.request.get('new_fields').split(',') if f <> ""]
            breakout = str(100/len(new_fields)) + "%"
            new_defaults = []
            for f in new_fields:
                new_defaults.append((f,breakout))
        this_user = users.get_current_user()
        if this_user <> None:
            mem_code = this_user.user_id() + "_table_fields"       
            memcache.set(mem_code, new_defaults)
        else:
            memcache.set("table_fields", new_defaults)
        self.response.out.write('good')

class AdvancedSearch(webapp2.RequestHandler):
    def get(self):
        v = {}
        v['model_properties'] = sorted([str(p) for p in models.sources.properties()])
        if self.request.get('action') == 'new_conditons':
            v['condition_index'] = str(int(self.request.get('filter_count')) + 1)
            tpath = '/templates/main/advanced_search_conditions.html'
        else:
            tpath = '/templates/main/advanced_search.html'
        self.response.out.write(render.load(tpath, v))
    def post(self):
        filter_limit = int(self.request.get('filter_count')) + 1
        filter_content = []
        translate_operators = {'EQUALS': '=', 'NOT EQUALS': '!=', 'CONTAINS':'CONTAINS', '':''}
        
        query_string = ""
        
        for i in range(1, filter_limit):
            andor_in_dom = 'row%i_andor' % (i)
            field_in_dom = 'row%i_field' % (i)
            operator_in_dom = 'row%i_operator' % (i)
            
            andor = self.request.get(andor_in_dom)
            field_name = self.request.get(field_in_dom)
            
            operator = translate_operators[self.request.get(operator_in_dom)]
               
            value_in_dom = '%i___%s' % (i, field_name)
            new_value = "'" + self.request.get(value_in_dom) + "'"
            if new_value == "":
                new_value = "NULL"
            
            if query_string == "":
                query_string += "WHERE %s %s %s" % (field_name, operator, new_value)    
            else:
                query_string += " %s %s %s %s" % (andor, field_name, operator, new_value)
        
        url = '/search?qt=dstore&view=table&nav=home&query_string=' + urllib.quote(query_string)
        self.response.out.write(url)