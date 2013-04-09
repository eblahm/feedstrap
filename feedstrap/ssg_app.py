import fix_path
fix_path.f()
import webapp2
import models
import string
from google.appengine.ext import db
import urllib
from datetime import datetime
import operator
import render
import search_tools as mst
import date_tools as my_date_tools


class TrendsHandler1(webapp2.RequestHandler):
  def get(self):  
    v = {}
    v['nav'] = 'trends'
    v['title'] = 'Popular Issues Report'
    map = {}
    for i in models.sources.all():
      if i.tags <> []:
        for t in i.tags:
          try:
            map[t] = map[t] + 1
          except:
            map[t] = 1
    v['sorted_tags'] = sorted(map.iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
    
    self.response.out.write(render.load('/templates/ssg_app/ssg_app.html', v))

class TrendsHandler2(webapp2.RequestHandler):
  def get(self):
    v = {'title': "Breakout"}
    conditions_raw = self.request.GET.getall('condition')
    conditions_raw.sort()
    v['crumbs'] = ""
    all_conditions = ""
    last = len(conditions_raw)
    x = 1
    for i in conditions_raw:
      data_list = string.split(i, ",,")
      if all_conditions == "":
        all_conditions += "condition=" + i
      else:
        all_conditions += "&condition=" + i
      con_ref = "/pir_breakout?%s" % (all_conditions)
      if x == last:
        arrow = ''
      else:
        arrow = ' <span class="divider"><i class="icon-arrow-right"></i></span>'
      v['crumbs'] += '<li><a href="%s">%s:%s</a>%s</li>' % (con_ref, data_list[1], data_list[2], arrow)
      x += 1
    v['this_con_num'] = int(conditions_raw[-1][0]) + 1
    q = models.sources.all()
    for i in conditions_raw:
      data_list = string.split(i, ",,")
      query_string = "%s =" % (data_list[1])
      q.filter(query_string, data_list[2])
    
    link_title = []
    maps = {'keywords_map':{},
            'concepts_map':{},
            'tags_map':{},}
    for i in q:
      if (i.link, i.title) not in link_title:
        link_title.append((i.link, i.title))
      
      ref = {'keywords_map':i.keywords,
             'concepts_map':i.concepts,
             'tags_map':i.tags}

      for m in ref:
        if ref[m] <> None:
          for t in ref[m]:
            try:
              maps[m][t] = maps[m][t] + 1
            except:
              maps[m][t] = 1
    v['all_conditions'] = all_conditions          
    v['concepts'] = sorted(maps['concepts_map'].iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
    v['keywords'] = sorted(maps['keywords_map'].iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
    v['tags'] = sorted(maps['tags_map'].iteritems(), key=operator.itemgetter(1), reverse=True)[:10]
    v['link_title'] = link_title

    self.response.out.write(render.load('/templates/ssg_app/pir_breakout.html', v))
