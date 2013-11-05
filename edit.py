import pytz
import json
from datetime import datetime
import urllib
from util import en, get_reports_with_permissions

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.core.context_processors import csrf
from filter import get_tags

from models import Resource, ResourceForm, Topic, Tag
import models
import render


def get_tags_from_names(tags_string):
    tags = []
    if tags_string.strip():
        for tname in [name.strip() for name in tags_string.split(',')]:
            tag, created = models.Tag.objects.get_or_create(name=tname)
            tags.append(tag)
    return tags

def save_resource(rec, data):
    lists = dict(data.lists())
    rec.title = en(data['title'])
    rec.description = en(data['description'])
    rec.relevance = en(data['relevance'])
    rec.tags = get_tags_from_names(data.get('tags', ''))
    rec.reports = [models.Report.objects.get(pk=ipk) for ipk in lists.get('reports', [])]
    rec.topics = [models.Topic.objects.get(pk=ipk) for ipk in lists.get('topics', [])]
    rec.save()


def write_access(rec, user):
    WA = False
    if user.is_authenticated():
        if user.is_staff:
            WA = True
        else:
            feeds = [f for f in rec.feeds.all()]
            postitq = models.PostIt.objects.filter(user=user)
            if postitq.count() == 0:
                this_user_feed = []
            else:
                this_user_feed = [postitq[0].feed]
            WA = feeds == this_user_feed
    return WA

def delete_access(rec, user):
    DA = False
    if user.is_authenticated():
        feeds = [f for f in rec.feeds.all()]
        postitq = models.PostIt.objects.filter(user=user)
        if postitq.count() == 0:
            this_user_feed = []
        else:
            this_user_feed = [postitq[0].feed]
        DA = feeds == this_user_feed
    return DA

def create_new_postit(user):
    feed = models.Feed(
        url = "http://feedstrap.vacloud.us/rss?feeds=",
        name = "%s Post It" % (user.username),
        user = user,
        description = "postit",
        last_updated = datetime.now()
    )
    feed.save()
    feed.url += str(feed.pk)
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
        rec_key = request.GET.dict()['k']
        rec = Resource.objects.get(pk=rec_key)
        v['rec'] = rec
        v.update(csrf(request))
        v['topics'] = Topic.objects.all().order_by('name')
        v['reports'] = get_reports_with_permissions(request.user, 'edit')
        template_file = 'main/forms/basic.html'
        return render.response(request, template_file, v)
    elif request.method == "POST":
        rec = Resource.objects.get(pk=int(request.POST['pk']))
        response_data = {}
        if write_access(rec, request.user):
            save_resource(rec, request.POST)
            now_est = datetime.now().replace(tzinfo=pytz.timezone('America/New_York'))
            message = '<em>updated %s</em>' % (now_est.strftime('%I:%M:%S%p'))
            message = message.lower() + " EST"
            response_data['id'] = 'ar_%s' % (rec.pk)
            response_data['ajax_html'] = render.load('main/list_view_article.html', 
                {'i': rec, 'auth': True, 'authorized_reports': get_reports_with_permissions(request.user, 'see')})
            response_data['save_status'] = message
            json_response = json.dumps(response_data)
            return HttpResponse(json_response)
        else:
            response_data['save_status'] = '<br><em>You are not authorized to edit this record.</em>'
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
                )
                rec.save()
            else:
                rec = recq[0]

            if rec.feeds.filter(pk=feed.pk).count() == 0:
                rec.feeds.add(feed)
                for rpt in feed.reports.all():
                    rec.reports.add(rpt)
                rec.save()

            save_resource(rec, request.POST)

            return HttpResponse("/q?feeds=" + str(feed.pk))
        else:
            return HttpResponseRedirect('/signin?redirect=%s' % (urllib.quote(request.get_full_path())))
    if request.method == "GET" or errors == True:
        errors = False
        v = {}
        if request.user.is_authenticated():
            g = request.GET
            recq = Resource.objects.filter(link=g['l'])
            if recq.count() == 0:
                rec = Resource(title=g.get('t', 'Untitled'),
                               link=g['l'],
                               description=g.get('d', ''),
                               date=datetime.now())
            else:
                rec = recq[0]
            v['rec'] = rec
            v.update(csrf(request))
            v['topics'] = Topic.objects.all().order_by('name')
            v['reports'] = get_reports_with_permissions(request.user, 'edit')
            v['all_tags'] = get_tags()
            v['postit'] = True
            v['feed'] = models.PostIt.objects.get(user=request.user).feed

            template_file = 'main/forms/post_it.html'
            return render.response(request, template_file, v)
        else:
            return HttpResponseRedirect('/signin?redirect=%s' % (urllib.quote(request.get_full_path())))


def delete(request):
    link = request.REQUEST['l']
    rec = Resource.objects.get(link=str(link))
    if delete_access(rec, request.user) and request.method == "POST":
        rec.delete()
        return HttpResponse("deleted")
    else:
        return HttpResponse("not authorized")

@login_required
@require_POST
def edit_link(request, action):

    user_xtd = models.PostIt.objects.filter(user=request.user)
    if not user_xtd:
        user_xtd = create_new_postit(request.user)
    else:
        user_xtd = user_xtd.get()

    if action == 'save':
        params = request.POST.copy()
        params.pop('csrfmiddlewaretoken')
        params.pop('name')
        params.pop('redirect')

        if request.POST.get('pk', None):
            params.pop('pk')
            sbar_link = models.SidebarLink.objects.get(pk=request.POST['pk'])
            sbar_link.name = request.POST['name']
            sbar_link.save()
        else:
            position = user_xtd.sidebar_links.all().count() + 1
            sbar_link = models.SidebarLink(
                name=request.POST['name'],
                parameters="",
                position=position,
                for_all_users=False
            )
            sbar_link.save()
            user_xtd.sidebar_links.add(sbar_link)

        sbar_link.parameters = render.encode_params(params)
        sbar_link.save()
        return HttpResponseRedirect('/?' + sbar_link.parameters)
    elif action == 'delete':
        sbar_link = models.SidebarLink.objects.get(pk=request.POST['pk'])
        user_xtd.sidebar_links.remove(sbar_link)
        user_xtd.save()
        sbar_link.delete()
        return HttpResponse('deleted!')
    else:
        return render.not_found(request)

