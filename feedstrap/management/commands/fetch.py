import os
import sys, traceback
import urllib2
import urllib
import pytz
from time import mktime
from datetime import datetime, timedelta
import xml.etree.ElementTree as etree

from goose import Goose
from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from cStringIO import StringIO

from ssg_site import feedparser, AlchemyAPI
from feedstrap import models
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from ssg_site import config, settings


def convert_pdf(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'ascii'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

    fp = file(path, 'rb')
    process_pdf(rsrcmgr, device, fp)
    fp.close()
    device.close()

    str = retstr.getvalue()
    retstr.close()
    return str

def normalize(x):
    if isinstance(x, unicode):
        return x.encode('ascii', 'xmlcharrefreplace')
    else:
        return str(x)

def extract_save_content(g, r):
    if r.link[-3:] == 'pdf':
        article_page = urllib2.urlopen(r.link)
        pdf_data = article_page.read()
        fn = settings.MEDIA_ROOT + r.title
        if fn[-4:] != '.pdf':
            fn += ".pdf"
        new_file = file(fn, 'wb')
        new_file.write(pdf_data)
        new_file.close()
        text = convert_pdf(fn)
    else:
        article = g.extract(url=r.link)
        text = article.cleaned_text
    r.content = normalize(text)
    r.save()
    return r


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        try:
            g = Goose()
            ## Query fetches in ascending order according to when feeds were last updated
            feeds_query = models.Feed.objects.filter(fetching=True).order_by('last_updated')
            for feed in feeds_query:
                parsed_feed = feedparser.parse(feed.url)
                # query for latest database item according to this particular feed
                ## The latest item in the RSS feed is compared with latest item in the database to determine
                ## weather or not a new item is present, further processing will happen to determine if the links are actually new
                try:
                    most_recent_from_db = models.Resource.objects.filter(feeds__pk=feed.pk).order_by("-date")[0].date
                except:
                    most_recent_from_db = datetime(1901, 12, 25)
                most_recent_from_db = most_recent_from_db.replace(tzinfo=pytz.utc)

                if len(parsed_feed.entries) > 0:
                    most_recent_from_feed = datetime.fromtimestamp(mktime(parsed_feed.entries[0].published_parsed))
                    most_recent_from_feed = most_recent_from_feed.replace(tzinfo=pytz.utc)
                else:
                    continue
                if most_recent_from_db < most_recent_from_feed:
                    ## new items should now be present
                    for item in parsed_feed.entries:
                        ## ignore previously added links.
                        logq = models.LinkLog.objects.filter(feeds=feed)
                        logq = logq.filter(link=item.link)
                        if logq.count() > 0:
                            continue
                        ## check membership in Resource Table
                        membership_query = models.Resource.objects.all().filter(link=item.link)
                        if membership_query.count() == 0:
                            dt = datetime.fromtimestamp(mktime(item.published_parsed))
                            dt = dt.replace(tzinfo=pytz.utc)
                            r = models.Resource(title=item.title,
                                                link=item.link,
                                                date=dt,
                                                description=item.description)
                            r.save()
                            r.feeds.add(feed)
                            r.save()
                        else:
                            r = membership_query.get()
                        if feed not in r.feeds.all():
                            r.feeds.add(feed)
                        for tag in feed.tags.all():
                            if tag not in r.tags.all():
                                r.tags.add(tag)
                        for office in feed.offices.all():
                            if office not in r.offices.all():
                                r.offices.add(office)
                        for report in feed.reports.all():
                            if report not in r.reports.all():
                                r.reports.add(report)
                        for topic in feed.topics.all():
                            if topic not in r.topics.all():
                                r.topics.add(topic)
                        r.save()
                        log = models.LinkLog(link=item.link)
                        log.save()
                        log.feeds.add(feed)
                        log.save()
                        try:
                            r = extract_save_content(g, r)
                        except:
                            self.stdout.write('TEXT EXTRACTION ERROR -- %s -- "%s"' % (feed.name, r.title[:20]))
                            traceback.print_exc(file=sys.stdout)
                        self.stdout.write('%s -- %s -- "%s"' % (datetime.now().strftime('%d %b %y %I:%M:%S%p'), feed.name, r.title[:20]))

            # now update the postit button content
            dayago = datetime.now() - timedelta(days=1)
            dayago = dayago.replace(tzinfo=pytz.utc)
            for p in models.PostIt.objects.all():
                postit_q = models.Resource.objects.filter(feeds=p.feed).filter(date__gte=dayago)
                for pi in postit_q:
                    if not pi.content:
                        try:
                            pi = extract_save_content(g, pi)
                            self.stdout.write('%s -- CONTENT SAVED -- %s -- "%s"' % (datetime.now().strftime('%d %b %y %I:%M:%S%p'), p.feed.name, pi.title[:20]))
                        except:
                            pi.content = "-"
                            pi.save()
                            self.stdout.write('TEXT EXTRACTION ERROR -- %s -- "%s"' % (p.feed.name, pi.title[:20]))
                            traceback.print_exc(file=sys.stdout)
        except:
            er = sys.exc_info()[-1]
            traceback.print_exc(file=sys.stdout)
            tb_list = traceback.format_tb(er)
            traceback_email = ''
            for e in tb_list:
                traceback_email += e
            send_mail('upload error',
                      traceback_email,
                      'vaphshalbem@localhost',
                      ['matthew.c.halbe@gmail.com'])







