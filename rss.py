from django.http import HttpResponse
from search import AdvancedSearch
import PyRSS2Gen


def main(request):
    AS = AdvancedSearch()
    results = AS.get_results(request.GET)[:20]
    rss_items = []
    for i in results:
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