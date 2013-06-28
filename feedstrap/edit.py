import pytz
import json
from datetime import datetime
import urllib

from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.core.context_processors import csrf

from models import Resource, ResourceForm, Topic, Tag
import models
import render


def en(s):
    if isinstance(s, unicode):
        return s.encode('ascii', 'xmlcharrefreplace')
    else:
        return str(s)

def get_tags():
    tag_cache = cache.get('all_tags')
    if tag_cache == None:
        all_tags = sorted([t for t in Tag.objects.all()])
        cache.set('all_tags', all_tags)
    else:
        all_tags = tag_cache
    return all_tags

def save_tags(rec, tags_list):
    tag_inputs = [t.strip() for t in tags_list]
    for tag in rec.tags.all():
        if tag.name not in tag_inputs:
            rec.tags.remove(tag)
            rec.save()
            if Resource.objects.filter(tags=tag).count() == 0:
                tag.delete()
        if tag.name == "":
            rec.tags.remove(tag)
    for tag in tag_inputs:
        if tag != "":
            try:
                tag_rec = models.Tag.objects.get(name=tag)
            except:
                tag_rec = models.Tag.objects.create(name=tag)
            rec.tags.add(tag_rec)
    return True

def save_manytomany(rec, property, key_list):
    if key_list in [[""], "", None]:
        key_list = []
    mmField = getattr(rec, property)
    for mm in mmField.all():
        mmField.remove(mm)
    for k in key_list:
        mmRec = getattr(models, property.title()[:-1]).objects.get(pk=int(k))
        mmField.add(mmRec)
    return True

def save_wr_topic_tags(rec, request):
    data_lists = dict(request.POST.lists())
    wrr = models.Report.objects.get(name="Weekly Reads")
    if request.POST.get("weekly_reads", "") == "on":
        rec.reports.add(wrr)
    else:
        rec.reports.remove(wrr)
    rec.save()
    save_manytomany(rec, 'topics', data_lists.get('topics', []))
    tags_list = data_lists.get('tags', [""])[0].split(',')
    save_tags(rec, tags_list)
    return rec

def create_new_postit(user):
    feed = models.Feed(
        url = "http://feedstrap.vacloud.us/rss?feeds=",
        name = "%s Post It" % (user.username),
        owner = "%s" %  (user.first_name),
        description = "postit",
        last_updated = datetime.now()
    )
    feed.save()
    feed.url += str(feed.pk)
    if user.first_name in ['James', 'Matt', 'Sharaelle', 'Joe', 'Thomas']:
        feed.offices.add(models.Office.objects.get(name='SSG'))
    feed.save()
    postit = models.PostIt(
        user = user,
        feed = feed
    )
    postit.save()
    return postit


def main(request):
    if request.method == "GET":
        v = {}
        v['all_tags'] = get_tags()
        rec_key = request.GET.dict()['k']
        rec = Resource.objects.get(pk=rec_key)
        rec.all_reports = [r.pk for r in rec.reports.all()]
        v['rec'] = rec
        v.update(csrf(request))
        v['resource_form'] = ResourceForm(instance=rec)
        v['topics'] = Topic.objects.all()
        template_file = '/main/forms/basic.html'
        return render.response(request, template_file, v)
    elif request.method == "POST":
        response_data = {}
        if not request.user.is_authenticated():
            response_data['save_status'] = 'You are not authorized to edit this record. If this is a mistake, <a href="/admin">please login</a>'
            json_response = json.dumps(response_data)
            return HttpResponse(json_response)
        else:
            rec = Resource.objects.get(pk=int(request.POST['pk']))
            rec.title = en(request.POST['title'])
            rec.description = en(request.POST['description'])
            rec.relevance = en(request.POST['relevance'])
            rec = save_wr_topic_tags(rec, request)
            now_est = datetime.now().replace(tzinfo=pytz.timezone('America/New_York'))
            message = '<em>updated %s</em>' % (now_est.strftime('%I:%M:%S%p'))
            message = message.lower() + " EST"
            response_data['id'] = 'ar_%s' % (rec.pk)
            response_data['ajax_html'] = render.load('/main/list_view_article.html', {'i': rec, 'auth': True})
            response_data['save_status'] = message
            json_response = json.dumps(response_data)
            return HttpResponse(json_response)

def add_new(request):
    errors = False
    v = {}
    if request.method == "POST":
        if request.user.is_authenticated():
            user = request.user
            postitq = models.PostIt.objects.filter(user=user)
            if postitq.count() == 0:
                postit = create_new_postit(user)
                feed = postit.feed
            elif postitq.count() == 1:
                feed = postitq[0].feed
            recq = Resource.objects.filter(link=request.POST['link'])
            if recq.count() == 0:
                rec = Resource(
                    date = datetime.now(),
                    title = en(request.POST['title']),
                    link = en(request.POST['link']),
                    description = en(request.POST['description']),
                    relevance = en(request.POST['relevance']),
                )
                rec.save()
                save_manytomany(rec, 'offices', [o.pk for o in feed.offices.all()])
            else:
                rec = recq[0]
                rec.title = en(request.POST['title'])
                rec.description = en(request.POST['description'])
                rec.relevance = en(request.POST['relevance'])
                rec.save()

            if rec.feeds.filter(pk=feed.pk).count() == 0:
                rec.feeds.add(feed)
                rec.save()
                all_offices = [o.pk for o in feed.offices.all()] + [o.pk for o in rec.offices.all()]
                save_manytomany(rec, 'offices', list(set(all_offices)))
                
            rec = save_wr_topic_tags(rec, request)
            return HttpResponse("/q?feeds=" + str(feed.pk))
        else:
            return HttpResponseRedirect('/signin?redirect=%s' % (urllib.quote(request.get_full_path())))
    if request.method == "GET" or errors == True:
        errors = False
        v = {}
        if request.user.is_authenticated():
            v['all_tags'] = get_tags()
            g = request.GET
            recq = Resource.objects.filter(link=g['l'])
            if recq.count() == 0:
                rec = Resource(title=g['t'], link=g['l'], description=g['d'], date=datetime.now())
                v['topics_pks'] = []
                v['tags'] = ""
                v['wr'] = False
            else:
                rec = recq[0]
                v['topics_pks'] = [t.pk for t in rec.topics.all()]
                v['tags'] = ", ".join([t.name for t in rec.tags.all()])
                if rec.reports.filter(name="Weekly Reads").count() > 0:
                    v['wr'] = True
            v['rec'] = rec
            v.update(csrf(request))
            v['resource_form'] = ResourceForm(instance=rec)
            v['topics'] = Topic.objects.all()
            template_file = '/main/forms/post_it.html'
            return render.response(request, template_file, v)
        else:
            return HttpResponseRedirect('/signin?redirect=%s' % (urllib.quote(request.get_full_path())))
            
            
def add_simple(request):
    js = ""
    if request.user.is_authenticated():
        user = request.user
        postitq = models.PostIt.objects.filter(user=user)
        if postitq.count() == 0:
            postit = create_new_postit(user)
            feed = postit.feed
        elif postitq.count() == 1:
            feed = postitq[0].feed
        g = request.GET
        recq = Resource.objects.filter(link=g['l'])
        if recq.count() == 0:
            rec = Resource(title=en(g['t']), link=en(g['l']), description=en(g['d']), date=datetime.now())
            rec.save()
            save_manytomany(rec, 'offices', [o.pk for o in feed.offices.all()])
        else:
            rec = recq[0]
        if rec.feeds.filter(pk=feed.pk).count() == 0:
            rec.feeds.add(feed)
            rec.save()
        return HttpResponse("alert('saved!')")
    else:
        return HttpResponse("alert('Please Log into FeedStrap before attempting to Post links')")
            
