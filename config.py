import os
import manage 

app_root = os.path.abspath(os.path.dirname(manage.__file__))

# is the Solr Server configured for full text search?
solr_enabled = True

# how many search results per page
per_page_limit = 10