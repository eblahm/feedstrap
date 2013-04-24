from django.http import HttpResponse
from filter import apply_filter
from ssg_site import PyRSS2Gen
import datetime


def main(request):
    v = {}
    v.update(apply_filter(request))
    rss_items = []
    for i in v['results']:
        item = PyRSS2Gen.RSSItem(title=i.title,
                                 link=i.link,
                                 description=i.description,
                                 guid="",
                                 pubDate=i.date,
        )
        rss_items.append(item)

    rss = PyRSS2Gen.RSS2(title="Feedstrap Query",
                         link="",
                         description="content from SSG",
                         items=rss_items
    )

    response = HttpResponse(content_type='application/rss+xml')
    response.write(rss.to_xml())
    return HttpResponse(response)