import os
import urllib2
import pytz
from time import mktime
from datetime import datetime
import xml.etree.ElementTree as etree
from ssg_site import feedparser, AlchemyAPI
from feedstrap import models
from django.core.management.base import BaseCommand, CommandError
from ssg_site import config


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ## Query fetches in ascending order according to when feeds were last updated
        feeds_query = models.Feed.objects.all().order_by('last_updated')
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
                        try:
                            page = urllib2.urlopen(item.link)
                            page_content = page.read()
                            alchemyObj = AlchemyAPI.AlchemyAPI()
                            alchemyObj.loadAPIKey(config.app_root + "/ssg_site/alcAPI.txt")
                            article_xml = alchemyObj.HTMLGetText(page_content, item.link)
                            text = etree.fromstring(article_xml).find("text").text
                            r.content = text
                            r.save()
                        except:
                            pass
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
                    self.stdout.write('%s -- "%s"' % (feed.name, r.title[:20]))
                #CommandError('Poll "%s" does not exist' % poll_id)


