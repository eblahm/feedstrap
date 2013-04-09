import fix_path
import webapp2
import models
import string
import search_tools as mst
import date_tools as my_date_tools
from datetime import datetime
from google.appengine.ext import db
import jinja2
import os
import re
import urllib2
from google.appengine.api import search
from google.appengine.api import users
from google.appengine.api import mail
from xlwt import *
import excel_tools as met
import operator

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(fix_path.app_root))

def get_rating(val, factor):
  rate_dic = {'intensity': (4, 10), 
              'relevance': (4, 10),
              'development': (2, 5),
              'impact':(3, 8)}
  if val >= 0:
    button = '<span class="label">LOW</span>'
    text = "LOW"
    num = 1
  if val >= rate_dic[factor][0]:
    button = '<span class="label label-warning">MED</span>'
    text = "MED"
    num = 2
  if val >= rate_dic[factor][1]:
    button = '<span class="label label-important">HIGH</span>'
    text = "HIGH"
    num = 3
  return {'button':button,'text':text,'num':num}

class change_criteria(webapp2.RequestHandler):
  def get(self):
    v = {"title": "Change Criteria Selectors"}
    m = {}
    for i in models.criteria.all():
      try:
        area = m[i.area]
      except:
        m[i.area] = {}
      try:
        group = m[i.area][i.group]
      except:
        m[i.area][i.group] = []
      m[i.area][i.group].append((str(i.key()), i.name))
    
    for area in m:
      # prep template
      v[area.replace(" ", "_")] = []
      
      sorted_gps = sorted(m[area].iteritems(), key=operator.itemgetter(0))
      
      for grp in sorted_gps:
        x = 0
        all_grp_keys = [item[0] for item in grp[1]]
        for item in grp[1]:
                  
          if x == 0:
            # first row has special info for formating purposes
            class row:
              group = grp[0]
              group_key = ",".join(all_grp_keys)
              name = item[1]
              name_key = item[0]
              length = len(grp[1])
            
            # avoid whitespace for template
            v[string.replace(area, " ", "_")].append(row)
            x += 1
          else:
            class row:
              name = item[1]
              name_key = item[0]
              
            # avoid whitespace for template
            v[string.replace(area, " ", "_")].append(row) 
            x += 1        
    template = jinja_environment.get_template('/templates/sp/sp_change_criteria.html')
    self.response.out.write(template.render(v))

class change_criteria_submit(webapp2.RequestHandler):
  def post(self):
    data = self.request.POST.items()
    for i in data:
      if i[0][:4] == "rec_":
        rec = db.get(i[0].replace("rec_", ""))
        rec.name = i[1]
        rec.put()
      elif i[0][:6] == "group_":
        all_recs = string.split(i[0].replace("group_", ""), ",")
        for dbk in all_recs:
          rec = db.get(dbk)
          rec.group = i[1]
          rec.put()
    self.redirect("/change_criteria")
                    
    
class sp(webapp2.RequestHandler):
  def get(self):
    v = {'title':"Weekly Reads Search"}
    user = users.get_current_user()
    if user:
      if user.nickname() == 'matthew.c.halbe':
        v['super_user'] = True 
    esil_q = models.topics.all()
    v['esil'] = []
    for t in esil_q:
       class issue:
         name = t.name
         db_key = str(t.key())
       v['esil'].append(issue)
    template = jinja_environment.get_template('/templates/sp/sharepoint.html')
    self.response.out.write(template.render(v))

class ESILHandler(webapp2.RequestHandler):
  def get(self):
    v = {'nav': "esil"}
    v['title'] = "Emerging Strategic Issues List"
    v['table'] = []
    show = self.request.get('show')
    q = models.topics.all()
    x = 0
    map = {}
    for i in q:
      rl = 0
      dev = ""
      rel = ""
      imp = ""
      tense = ""
      if i.options <> None:
        rl += len(i.options)
      if i.imperatives <> None:
        rl += len(i.imperatives)    
        rel = get_rating(rl, 'relevance')   
      if i.data_sources <> None:
        tense = get_rating(len(i.data_sources), 'intensity')
        groups = []
        try:
          for dbk in i.data_sources:
            group = db.get(dbk).group
            if group not in groups:
              groups.append(group)
        except:
          pass
        dev = get_rating(len(groups), 'development')                                 
      if i.capabilities <> None:
        imp = get_rating(len(i.capabilities), 'impact')  
      cl = []   
      comment_q = models.comments.all().filter("deleted =", False).ancestor(i.key())
      for c in comment_q:
        this = {}
        this['name'] = c.name
        this['org'] = c.org
        this['comment'] = c.comment
        this['db_key'] = str(i.key())
        this['c_key'] = str(c.key())
        if show == this['db_key']:
          this['comment_show'] = ''
        else:
          this['comment_show'] = 'display:none;' 
        cl.append(this)
        
      r = {}
      r['topic_name'] = i.name
      r['key'] = str(i.key())
      if i.description <> None:
        r['description'] = i.description
      r['comments'] = cl
      if show == r['key']:
        r['comment_show'] = ""
        r['pm_icon'] = 'minus'
      else:
        r['comment_show'] = 'display:none;'
        r['pm_icon'] = 'plus'
      r['intensity'] = tense['button']    
      r['development'] = dev['button']
      r['impact'] = imp['button']
      r['relevance'] = rel['button']
      this_score = rel['num'] + tense['num'] + dev['num'] + imp['num']
             
      v['table'].append((this_score, r))
    v['table'] = sorted(v['table'], reverse=True)
    template = jinja_environment.get_template('/templates/sp/esil.html')
    self.response.out.write(template.render(v))


    
class ESIL_Extend_Handler(webapp2.RequestHandler):
    def get(self, action):
        v = {'nav': "esil"}
        if action == 'sc':
            v['title'] = 'Scorecard'

            # USED to hold selected values
            c = {'Strategic Imperatives': [],
                'Strategic Options': [],
                'VA Capabilites':[],
                'Data Sources': []}

            # USED for Template output
            v['Strategic_Imperatives'] = []
            v['Strategic_Options'] = []
            v['VA_Capabilites'] = []
            v['Data_Sources'] = []
            v['relevance'] = ""
            v['intensity'] = ""
            v['development'] = ""
            v['impact'] = ""


            # if the topic already exists, the request will come with a db key
            dbk = self.request.get('rkey')
            if dbk <> '':
                rec = db.get(dbk)
                # put basic info into the template
                v['topic_name'] = rec.name
                v['description'] = rec.description
                v['rkey'] = dbk


                ####    Q data to determin previously selected items ###
                # rel is just a aggregation tool for duel field property
                rel = 0
                if rec.options <> None:
                    # Indicates previously selected items in this field
                    c['Strategic Options'] = rec.options

                    # Genergate Info for the Ratings bar
                    rel += len(rec.options)
                    v['relevance'] = get_rating(rel, 'relevance')['button']

                if rec.imperatives <> None:
                    c['Strategic Imperatives'] = rec.imperatives
                    rel += len(rec.imperatives)
                    v['relevance'] = get_rating(rel, 'relevance')['button']

                if rec.data_sources <> None:
                    c['Data Sources'] = rec.data_sources
                    v['intensity'] = get_rating(len(rec.data_sources), 'intensity')['button']

                    # Genergate More Info for the Ratings bar
                    groups = []
                    try:
                        for dbk in i.data_sources:
                            group = db.get(dbk).group
                            if group not in groups:
                                groups.append(group)
                    except:
                        pass
                    v['development'] = get_rating(len(groups), 'development')['button']


                if rec.capabilities <> None:
                    c['VA Capabilites'] = rec.capabilities
                    v['impact'] = get_rating(len(rec.capabilities), 'impact')['button']


            for area in c:
                # All Query to render full table
                q = models.criteria.all().filter('area =', area).order('group')

                # criteria model is one to many relationship between field
                # area map generates dict for relationships
                area_map = {}
                for i in q:
                    dbk = str(i.key())
                    try:
                        this_list = area_map[i.group]
                        this_list.append((i.name, dbk))
                    except:
                        area_map[i.group] = [(i.name, dbk)]
                sorted_gps = sorted(area_map.iteritems(), key=operator.itemgetter(0))
                for grp in sorted_gps:
                    area_map[grp[0]].sort()
                    x = 0
                    for n in area_map[grp[0]]:
                        if n[1] in c[area]:
                            ckd = 'checked="checked"'
                        else:
                            ckd = ''

                        if x == 0:
                            # first row has special info for formating purposes
                            class row:
                                group = grp[0]
                                name = n[0]
                                name_key = n[1]
                                length = len(area_map[grp[0]])
                                checked = ckd

                            # avoid whitespace for template
                            v[string.replace(area, " ", "_")].append(row)
                            x += 1
                        else:
                            class row:
                                group = grp[0]
                                name = n[0]
                                name_key = n[1]
                                checked = ckd
                            # avoid whitespace for template
                            v[string.replace(area, " ", "_")].append(row)
                            x += 1

            template = jinja_environment.get_template('/templates/sp/scorecard.html')
            self.response.out.write(template.render(v))
        elif action == 'tc':
            v['title'] = 'Topic Card'
            def build_string(dstore_rec):
                if dstore_rec <> None and dstore_rec <> [""]:
                    map = {}
                    for dbk in dstore_rec:
                        rec = db.get(dbk)
                        try:
                            present = rec.name
                        except:
                            continue
                        try:
                            clist = map[rec.group]
                            clist.append(rec.name)
                        except:
                            map[rec.group] = [rec.name]
                    html_string = '<ul class="unstyled">'
                    sorted_map = sorted(map.iteritems(), key=operator.itemgetter(0))
                    for i in sorted_map:
                        html_string += "<li><strong>%s</strong><ul>" % (i[0])
                        i[1].sort()
                        for a in i[1]:
                            html_string += '<li>%s</li>' % (a)
                        html_string += '</ul>'
                        html_string += '</li>'
                    html_string += '</ul>'
                    return html_string
                else:
                    return ""

            if self.request.get('rkey') <> '':
                rec = db.get(self.request.get('rkey'))
                v['topic_name'] = rec.name
                v['description'] = rec.description
                v['rkey'] = self.request.get('rkey')

                v['imperatives'] = build_string(rec.imperatives)
                v['options'] = build_string(rec.options)
                v['capabilities'] = build_string(rec.capabilities)
                v['data_sources'] = build_string(rec.data_sources)

                v['relevance'] = ""
                v['intensity'] = ""
                v['development'] = ""
                v['impact'] = ""

                rel = 0
                if rec.options <> None and rec.options <> [""]:
                    rel += len(rec.options)
                if rec.imperatives <> None and rec.imperatives <> [""]:
                    rel += len(rec.imperatives)
                    v['relevance'] = get_rating(rel, 'relevance')['button']
                if rec.data_sources <> None and rec.data_sources <> [""]:
                    v['intensity'] = get_rating(len(rec.data_sources), 'intensity')['button']
                    groups = []
                    for i in rec.data_sources:
                        g = string.split(i, "##")
                        if g[0] not in groups:
                            groups.append(g[0])
                    v['development'] = get_rating(len(groups), 'development')['button']
                if rec.capabilities <> None and rec.capabilities <> [""]:
                    v['impact'] = get_rating(len(rec.capabilities), 'impact')['button']
            v['comments'] = []
            rec_key = rec.key()
            comments_q = models.comments.all().filter('deleted =', False).ancestor(rec_key)
            for c in comments_q:
                n = {}
                n['name'] = c.name
                n['org'] = c.org
                n['comment'] = c.comment
                v['comments'].append(n)
            v['links'] = []
            query = models.sources.all().order('-date').filter('esil =', str(rec_key))
            for i in query:
                article_date = my_date_tools.datetorss(i.date)
                article_date_short = article_date[5:11] + " " + article_date[14:16]

                class r:
                    date = article_date_short
                    posted_by = i.posted_by
                    description = i.description
                    relevance = i.relevance
                    link = i.link
                    title = i.title
                v['links'].append(r)
            if self.request.get('export') == "word":
                v['render'] = 'export'
                self.response.headers['Content-Type'] = 'application/msword'
                self.response.headers['Content-disposition'] = str('attachment; filename="Topic Card - %s.doc"' % (v['topic_name']))
                template = jinja_environment.get_template('/templates/sp/topic_card.html')
                self.response.out.write(template.render(v))
            else:
                v['render'] = 'page'
                template = jinja_environment.get_template('/templates/sp/topic_card.html')
                self.response.out.write(template.render(v))
        elif action == 'dc':
            this_key = self.request.get('rkey')
            rec = db.get(this_key)
            rec.delete()

            template = jinja_environment.get_template('/templates/sp/deleted.html')
            self.response.out.write(template.render(v))
        else:
            self.response.out.write('404: Not Found')
    def post(self, action):
        if action == 'sc':
            if self.request.get('rkey') <> "":
                new = db.get(self.request.get('rkey'))
                new.name = mst.ude(self.request.get('topic_name'))
            else:
                new = models.topics(name = mst.ude(self.request.get('topic_name')))

            if len(self.request.get_all('dss')) <> 0:
                new.data_sources = self.request.get_all('dss')
            else:
                new.data_sources = ['']
            if len(self.request.get_all('caps')) <> 0:
                new.capabilities = self.request.get_all('caps')
            else:
                new.capabilities = ['']
            if len(self.request.get_all('sopts')) <> 0:
                new.options = self.request.get_all('sopts')
            else:
                new.options = ['']
            if len(self.request.get_all('sis')) <> 0:
                new.imperatives = self.request.get_all('sis')
            else:
                new.imperatives = ['']
            if self.request.get('description') <> "":
                new.description = mst.ude(self.request.get('description'))
            else:
                new.description = None
            new.put()
            subject= 'ESIL Topic "%s" was edited!' % (new.name)
            body= 'ESIL "%s" was edited!' % (new.name)
            sender="Matt Halbe <matthew.c.halbe@gmail.com>"
            to="Matt Halbe <matt.halbe@va.gov>"
            mail.send_mail(sender, to, subject, body)
            self.redirect("/esil")
        elif action == 'add_comment':
            db_key = self.request.get('db_key')
            this_parent = db.get(db_key)
            sender ="ESIL Update <matthew.c.halbe@gmail.com>"
            if self.request.get('action') == 'delete':
                rec = db.get(self.request.get('c_key'))
                if rec.comment <> None:
                    rec.deleted = True
                    rec.put()
                    this_name = rec.name
                    this_org = rec.org
                    this_comment = rec.comment
                    to="Matt Halbe <matt.halbe@va.gov>"
                    subject='Comment Deleted "%s"' % (this_parent.name)
                    body= """The following comment was deleted: %s from %s commented: "%s" """ % (this_name, this_org, this_comment)
                    mail.send_mail(sender, to, subject, body)
                self.response.out.write("good")
            else:
                this_name = self.request.get('name')
                this_org = self.request.get('org')
                this_comment = self.request.get('comment')

                new_comment = models.comments(name = this_name,
                                              comment = this_comment,
                                              org = this_org,
                                              date = datetime.now(),
                                              deleted = False,
                                              parent = this_parent)
                new_comment.put()
                if this_org <> "":
                    this_org = " from " + this_org
                distro = ["Matt Halbe <matt.halbe@va.gov>"] #, "Blockwood, James-Christian <james-christian.blockwood@va.gov>"]
                for e in distro:
                    subject='New Comment on "%s"' % (this_parent.name)
                    body= """On %s, %s%s commented:
    "%s"

    See the comment here: http://vaww.vaco.portal.va.gov/sites/OPP/policy/ssg/esil/default.aspx
                    """ % (datetime.now().strftime('%m-%d-%Y'), this_name, this_org, this_comment)
                    mail.send_mail(sender, e, subject, body)


                re_url = "/esil?show=" + db_key
                self.redirect(re_url)
        else:
            self.response.out.write('404: Not Found')


class sp_search(webapp2.RequestHandler):
  def get(self):      
    v = {}
    nothings = [[], [""], [None], None, ""]

    query_type = self.request.get('query_type')

    if query_type == "text":
      term = self.request.get('search_term')
      v['term'] = term
      if term <> "":
        term += ' AND report:Weekly Reads'
      else:
        term = 'report:Weekly Reads'
      v['full_term'] = term
      c = self.request.get('c')
      if c <> "":
        curs = search.Cursor(web_safe_string=c)
      else:
        curs = search.Cursor()
      query = mst.my_finder(term, 10, curs, [mst.score_desc]) 
      try:  
        next_cursor = query.cursor.web_safe_string
        v['next_cursor'] = next_cursor
      except:
        pass  
    
    elif query_type == "tag":
      query = models.sources.all().filter('tags_list =', self.request.get('tag'))
      v['term'] = "tags:%s" % (self.request.get('tag'))
      v['full_term'] = v['term'] + " AND report:Weekly Reads"
    else:
      v['term'] = ""
      query = []
    
      
      
    if v['term'] <> "":
      new_search_log = models.search_log(search_term = v['term'],
                                       date = datetime.now(),
                                       referal = "Weekly Reads Sharepoint")
      user = users.get_current_user()
      if user <> None:
        new_search_log.user = user.nickname()
        new_search_log.put()
         
    results = []
    for i in query:
      if query_type == "text":
        rec = db.get(i.doc_id)
      else:
        rec = i
      article_date = my_date_tools.datetorss(rec.date)
      article_date_short = article_date[5:11] + " " + article_date[14:16]
      
      class r:
        date = article_date_short
        posted_by = rec.posted_by
        description = rec.description
        relevance = rec.relevance
        link = rec.link
        title = rec.title
        db_key = str(rec.key())
        if rec.tags_list not in nothings:
          tags_list = []
          for tag in rec.tags_list:
            tag_link = '<span class="btn-link live_tag" name="%s">%s</span>' % (tag, tag)
            tags_list.append(tag_link)
          tags = ", ".join(tags_list)
#        if rec.esil not in nothings:
#          esil_list = []
#          for issue_key in rec.esil:
#            topic_rec = db.get(issue_key)
#            esil_link = '<a href="/tc?rkey=%s">%s</a>' % (issue_key, topic_rec.name)
#            esil_list.append(esil_link)
          #esil = ", ".join(esil_list)
      results.append(r)
    if self.request.get('show_line') == "y":
      v['show_line'] = 'go'
      
    v['results'] = results
    
    template = jinja_environment.get_template('/templates/sp/ajax_sp_search.html')
    self.response.out.write(template.render(v))

class cl(webapp2.RequestHandler):
  def get(self):
    l = self.request.get('l')
    new_click = models.clicks(link = l,
                                  date = datetime.now(),
                                  referal = "Weekly Reads Sharepoint")
    user = users.get_current_user()
    if user:
      new_click.user = user.nickname()
    new_click.put()
    self.response.out.write("nice")


                                                     
class spexport(webapp2.RequestHandler):
  def get(self):                                                  
      wb = Workbook()
      esil_tab = wb.add_sheet('ESIL')
      numbered_tab = wb.add_sheet('ESIL Numbered')                                              
      details_tab = wb.add_sheet('ESIL Details')                                              
      tabs = {"esil_tab":{'obj': esil_tab, 
                          'headings': ["#", "Topic", "Description", "Intensity", "Development","Relevance","Impact"]},
              "numbered_tab":{'obj': numbered_tab, 
                              'headings': ["#", "Topic", "Description", "Intensity", "Development","Relevance","Impact", "Total"]},
              "details_tab":{'obj': details_tab, 
                             'headings': ["#", "Topic", "Description", "Data Sources", "Strategic Imperatives","Strategic Options","VA Capabilities"]}
              }
      esil_tab.write_merge(0,0,0,6,"Emerging Strategic Issues List",met.banner_style2)
      numbered_tab.write_merge(0,0,0,6,"ESIL Numbered",met.banner_style2)                                                
      details_tab.write_merge(0,0,0,6,"ESIL Details",met.banner_style2)
    
      for tab in tabs:                                             
        tabs[tab]['obj'].col(0).width = met.pix_convert(92)  
        tabs[tab]['obj'].col(1).width = met.pix_convert(270)
        tabs[tab]['obj'].col(2).width = met.pix_convert(96)                                                      
        tabs[tab]['obj'].col(3).width = met.pix_convert(96)                                                                                                      
        tabs[tab]['obj'].col(4).width = met.pix_convert(96)                                          
        tabs[tab]['obj'].col(5).width = met.pix_convert(96)                                                                                               
        tabs[tab]['obj'].col(6).width = met.pix_convert(96)                                                
        tabs[tab]['obj'].col(7).width = met.pix_convert(96)
      for tab in tabs:
        for i in range(0, len(tabs[tab]['headings'])):
           tabs[tab]['obj'].write(1, i, tabs[tab]['headings'][i], met.plain)   
      
                                                
      q = models.topics.all()  
              
      #name,description, options, data_sources, imperatives, capabilities                                                    
      #for i in q:
        # Main Tab Data Write     
        #esil_tab.write(1, 0, "#", met.plain)          


  
                                                      
      self.response.headers['Content-Type'] = 'application/ms-excel'
      self.response.headers['Content-Transfer-Encoding'] = 'Binary'
      
      self.response.headers['Content-disposition'] = 'attachment; filename="%s Emerging Strategic Issues List.xls"' % (datetime.now().strftime("%Y%m%d"))
      wb.save(self.response.out)

class wrexport(webapp2.RequestHandler):
  def get(self): 
    term = self.request.get('term')
    if self.request.get('x') == "1":   
      query = mst.my_finder(term, 300, search.Cursor(), [mst.score_desc])
      wb = Workbook()
      ws = wb.add_sheet('Results')
      standard_style = easyxf(
      'font: name Calibri;'
      'alignment: wrap True, vertical center;')
      
      banner_style = easyxf(
      'align: vertical center, horizontal center;'
      'font: height 400, name Calibri;'
      )
      clean_t = mst.ude(term).encode('ascii', 'ignore')
      clean_t = string.replace(string.replace(term, "report:Weekly Reads", "")," AND ", "")                   
      ws.write_merge(2,2,0,4,'Weekly Reads Database Search Results',banner_style)
      ws.row(0).height = 1000
      ws.write(0, 0, 'Date:')
      ws.write(0, 1, my_date_tools.datetorss(datetime.now()))
      ws.write(1, 0, 'Term:')
      ws.write(1, 1, clean_t)
      hsty = easyxf(
      'font: name Calibri, bold True;')
      t_start = 3
      ws.write(t_start, 0, 'Date', hsty)
      ws.col(0).width = 2000
      ws.write(t_start, 1, 'Title', hsty)
      ws.col(1).width = 5000
      ws.write(t_start, 2, 'Tags', hsty)
      ws.col(2).width = 4000
      ws.write(t_start, 3, 'Description', hsty)
      ws.col(3).width = 12000
      ws.write(t_start, 4, 'Relevance to VA', hsty)
      ws.col(4).width = 12000
      
      cs = easyxf(
      'font: name Calibri;'
      'alignment: wrap True, vertical center;')
      dsty = easyxf(
      'font: name Calibri;'
      'alignment: vertical center;',num_format_str='MM-DD-YY')
      hypstyle = easyxf('font: name Calibri, underline single, color blue;'
                        'alignment: wrap True, vertical center;')
      x = 4
      for i in query:
        r = db.get(i.doc_id)
        link_formula = 'HYPERLINK("%s","%s")' % (r.link, string.replace(r.title,'"',''))
        ws.write(x, 0, r.date, dsty)
        ws.write(x, 1, Formula(link_formula), hypstyle)
        ws.write(x, 2, mst.nn(r.tags), cs)
        ws.write(x, 3, mst.nn(r.description), cs)
        ws.write(x, 4, mst.nn(r.relevance), cs)
        x = x + 1            
      self.response.headers['Content-Type'] = 'application/ms-excel'
      self.response.headers['Content-Transfer-Encoding'] = 'Binary'
      self.response.headers['Content-disposition'] = 'attachment; filename="Weekly Reads Search %s.xls"' % (datetime.now().strftime("%Y%m%d"))
      wb.save(self.response.out)
    else:
      self.response.out.write('Determined Worker Intense Good worker Hard worker Terrific')  