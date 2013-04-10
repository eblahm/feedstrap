import os
import urllib2
from time import mktime
from datetime import datetime
import xml.etree.ElementTree as etree
from ssg_site import feedparser, AlchemyAPI
from feedstrap import models
from django.core.management.base import BaseCommand, CommandError




class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        ## Update 3 at a time
        ## Query fetches in ascending order according to when feeds were last updated
        feeds_query = models.Feed.objects.all().order_by('last_updated')
        for feed in feeds_query:
            self.stdout.write('fetching "%s"' % feed.name)
            parsed_feed = feedparser.parse(feed.url)
            # query for latest database item according to this particular feed
            ## The latest item in the RSS feed is compared with latest item in the database to determine
            ## weather or not a new item is present, futher processing will happen to determin in the links are actually new
            try:
                most_recent_from_feed = models.Resource.objects.all().filter(feed__pk=feed.pk).order_by("-date")[0].date
            except:
                # AKA no item from this feed yet in db
                most_recent_from_feed = datetime(1901,12,25)

            ## date test
            if most_recent_from_feed.time < parsed_feed.entries[0].published_parsed:
                ## new items should now be present
                for item in parsed_feed.entries:
                    found = 0
                    ## if a user has deleted the item it goes on the "Deleted" list.  These should be ignored.
                    if models.DeletedLink.objects.filter(link=item.link).count() > 0:
                        continue
                        ## check membership in Resource Table
                    membership_query = models.Resource.objects.all().filter(link=item.link)
                    feed_limited_query = membership_query.filter(feed__pk=feed.pk)
                    if feed_limited_query.count() > 0:
                        found += 1
                        if found > 4:
                            # minimize db queries
                            break
                    else:
                        if membership_query.count() == 0:
                            dt = datetime.fromtimestamp(mktime(item.published_parsed))
                            r = models.Resource(title=item.title,
                                                link=item.link,
                                                date=dt,
                                                description=item.description)
                            try:
                                page = urllib2.urlopen(item.link)
                                page_content = page.read()
                                alchemyObj = AlchemyAPI.AlchemyAPI()
                                alchemyObj.loadAPIKey("/Users/Matt/Dropbox/dev/ssg_site/ssg_site/alcAPI.txt")
                                article_xml = alchemyObj.HTMLGetText(page_content, item.link)
                                text = etree.fromstring(article_xml).find("text").text.encode('utf-8','ignore')
                                r.content = text
                            except:
                                pass
                            r.save()
                        else:
                            r = membership_query.get()

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
                        self.stdout.write('New Resource Added! -- "%s"' % r.title)
                #CommandError('Poll "%s" does not exist' % poll_id)


