import os

app_root = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])

# is the Solr Server configured for full text search?
solr_enabled = False

# how many search results per page
per_page_limit = 10