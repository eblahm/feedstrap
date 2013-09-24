import render
from models import Topic, Resource
from filter import apply_filter

from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.template import Template, Context
from django.core.mail import send_mail, mail_admins
from django.contrib.comments.views.comments import post_comment
from django_comments_xtd.models import XtdComment as Comment

from datetime import datetime
import csv
import urllib


def get_rating(val, factor):
    rate_dic = {'intensity': (15, 30),
                'relevance': (4, 10),
                'impact':(3, 8),}
    if val >= 0:
        button = '<span style="color:white">1</span><span class="label">LOW</span>'
    if val >= rate_dic[factor][0]:
        button = '<span style="color:white">2</span><span class="label label-warning">MED</span>'
    if val >= rate_dic[factor][1]:
        button = '<span style="color:white">3</span><span class="label label-important">HIGH</span>'
    return button


def all_comments(request, pk):
    topic = Topic.objects.get(pk=int(pk))
    context = Context({
        'topic': topic,
        'user': request.user,
        })
    mini_template = '{% load comments %}{% load comments_xtd %}{% render_comment_list for topic %}'
    raw_ajax_string = Template(mini_template).render(context=context)
    return HttpResponse(raw_ajax_string)


def single_topic(request, pk):
    v = {}
    topic = Topic.objects.filter(pk=int(pk))
    if request.user.is_authenticated() and topic:
        topic = topic.get()
        v['imperatives'] = [model_to_dict(t, fields=['name', 'category']) for t in topic.imperatives.all()]
        v['capabilities'] = [model_to_dict(c, fields=['name', 'category']) for c in topic.capabilities.all()]
        v['next'] = request.path + 'comments'

        rsearch = Resource.objects.filter(topics=topic).order_by('-date')
        topic.link_count = rsearch.count()
        topic.intensity = get_rating(rsearch.count(), 'intensity')
        topic.impact = get_rating(topic.capabilities.all().count(), 'impact')
        topic.relevance = get_rating(topic.imperatives.all().count(), 'relevance')

        v['topic'] = topic
        v['resources'] = rsearch
        v['get_url'] = request.GET.urlencode()
        return render.response(request, "main/esil/topic_card.html", v)
    else:
        return render.not_found(request)


def comment_handler(request):
    if request.user.is_authenticated():
        topic_pk = request.GET.get('object_pk', None)
        topic = Topic.objects.get(pk=topic_pk)
        subject = 'New Comment for ' + topic.name
        mail_admins(subject, subject)

        return post_comment(request)
    else:
        return HttpResponse('you must be logged in to post comments')


def delete_comment(request, comment_id):

    try:
        q = Comment.objects.filter(pk=int(comment_id)).get()
    except:
        q = False

    if request.user.is_authenticated() and q:
        topic_pk = q.object_pk
        q.is_removed = True
        q.save()
        # q.delete()
        return all_comments(request, topic_pk)
    else:
        return HttpResponse('error')



def all_topics(request):
    v = {}
    usr = request.user
    if request.user.is_authenticated():
        if usr.has_perm('feedstrap.view_all') or usr.is_staff or usr.is_superuser:
            q = Topic.objects.all()
        else:
            q = Topic.objects.filter(published=True)
        topics = []
        for t in q.order_by('name'):
            rsearch = Resource.objects.filter(topics=t)
            t.link_count = rsearch.count()
            t.intensity = get_rating(rsearch.count(), 'intensity')
            t.impact = get_rating(t.capabilities.all().count(), 'impact')
            t.relevance = get_rating(t.imperatives.all().count(), 'relevance')
            topics.append(t)
        v['topics'] = topics
        v['nav'] = 'esil'
        template_file = 'main/esil/main_view.html'
        return render.response(request, template_file, v)
    else:
        return HttpResponseRedirect('/signin?redirect=%s' % (urllib.quote(request.get_full_path())))

def weeklyreads(request):
    v = {}
    v.update(request.GET.dict())
    v['admin'] = request.user.is_authenticated()
    v.update(apply_filter(request, slice=False))
    v['next_offset'] = False
    template_file = 'main/weekly_reads/export_view.html'
    v['headline'] = 'Weekly Reads Report'
    v['subheadline'] = 'Prepared by Strategic Studies Group, Office of Policy'
    v['date'] = datetime.now().strftime('%x')
    v['results'] = v['results'].order_by('tags__name')[:100]
    dedup = []
    for r in v['results']:
        if r not in dedup:
            dedup.append(r)
    v['results'] = dedup
    response = HttpResponse(content_type='application/msword')
    response['Content-Disposition'] = 'attachment; filename="%s SSG Weekly Reads.doc"' % (datetime.now().strftime('%y%m%d'))
    ms_doc = render.load(template_file, v)
    response.write(ms_doc)
    return response


def en(s):
    if isinstance(s, unicode):
        return s.encode('ascii', 'xmlcharrefreplace')
    else:
        return str(s)


def export_csv(request):
    v = {}
    v.update(apply_filter(request, per_page_limit=5000))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="search results.csv"'

    writer = csv.writer(response)
    header_row = ['feed urls', 'date', 'title', 'link', 'tags', 'description', 'relevance']
    writer.writerow(header_row)
    results = v['results'][:100]
    for rec in results:
        row = []
        row.append(', '.join([en(f.url) for f in rec.feeds.all()]))
        row.append(rec.date.strftime("%Y-%m-%dT%H:%M:%S"))
        row.append(en(rec.title))
        row.append(en(rec.link))
        row.append(', '.join([en(t.name) for t in rec.tags.all()]))
        row.append(en(rec.description)[:131071])
        row.append(en(rec.relevance)[:131071])
        writer.writerow(row)
    return response
