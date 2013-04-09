import string
from datetime import datetime
import xml.etree.ElementTree as etree
import urllib2
import json
import re
from feedstrap import models

## Cron is set up to run this script every 10 minutes  
def update_db():
  ## eventual return object which will communicate the status of this update

  ## Update 3 at a time
  ## Query fetches in ascending order according to when feeds were last updated
  feeds_query = models.feeds.all().order("last_updated").fetch(limit=3, read_policy=db.STRONG_CONSISTENCY)
  
  for feed in feeds_query:
    update_info[feed.url] = []
    ## a bacic url page load for the feed will not usually fail, but just incase it does, 
    ## error will not prevent the other 5 feeds from being updated
    try:
      req = urllib2.Request(feed.url)
      response = urllib2.urlopen(req)
    except: 
      feed.last_updated = datetime.now()
      feed.put()
      continue
    page = response.read()
    
    
    ## Sometimes etree can't read the xml, I still haven't found a solution for these cases
    ## I assume that the xml is just improperly formed
    try:
      xml_root = etree.fromstring(page)
    except:
      this_d = 'broken xml: ' + str(feed.url)
      error_test = models.my_errors.all().filter('description =', this_d).count()
      if error_test == 0:
        new_error = models.my_errors(description = this_d, date = datetime.now())
        new_error.put()
      feed.last_updated = datetime.now()
      feed.put()
      continue
      
    ## basic etree xml processing
    feed_channel = xml_root.find("channel")
    items = feed_channel.findall("item")  
    
    # query for latest database item according to this particular feed
    ## The latest item in the RSS feed is compared with latest item in the database to determine
    ## weather or not a new item is present, futher processing will happen to determin in the links are actually new
    sources_query = models.sources.all().filter("feed_url =", feed.url).order("-date")
  
    # If the feed is brand new, and has never had items added to the database the query will return nothing
    ## in this case, a date comparison of the latest item would cause an error 
    ## to avoid an error I generate a fake date so that the new item test always returns true
    ## qd represents query date
    if sources_query.count() == 0:
      qd = datetime(1950,12,12,12,12,12)
    else:
      qd = sources_query.get().date
      
    ## processing rss date sometimes produces errors  
    ## still looking for a solution
    try:
      item_qd = mdt.rssdateconvert(items[0].find("pubDate").text)
    except:
      item_qd = datetime(2050,12,12,12,12,12)
      this_d = 'error when trying to process the date of the first item for the following feed: ' + str(feed.url)
      error_test = models.my_errors.all().filter('description =', this_d).count()
      if error_test == 0:
        new_error = models.my_errors(description = this_d, date = datetime.now())
        new_error.put()

    ## date test
    if qd < item_qd:
      ## new items should now be present
      ## empty list for items that i will eventually add to the database
      newitems = []
        
      ## CHECK FOR NEW LINKS
      ## 4 consecutive failures to find a new link will terminate loop to save datastore query calls
      unique_fail = 0
      for item in items:
        if unique_fail > 3:
          break
        try:
          item_link = item.find("link").text
        except:
          continue
        membership_check = models.sources.all().filter("feed_url =", feed.url).filter('link =', item_link).count(read_policy=db.STRONG_CONSISTENCY)          
        ## if a user has deleted the item in the datase it goes on the "Deleted" list.  
        ## These items should not be reentered into the databse
        deleted_check = models.deletedlinks.all().filter('link =', item_link).count(read_policy=db.STRONG_CONSISTENCY)
        
        ## run the test
        if membership_check == 0 and deleted_check == 0:
          newitems.append(item)
          unique_fail = 0
        else:
          unique_fail += 1

       
      for a in newitems:
        ##  create list via etree object
        achild = list(a)          
        ##  avoid non-ascii
        for b in achild:
          if b.text <> None and b.tag <> "link":
            b.text = b.text.encode('ascii', 'ignore')
          
        ##  avoid multiline title       
        this_link = a.find("link").text
        this_title = re.sub(r"\r?\n"," ", a.find("title").text)
      
        ##  instanciate "sources" databstore model, link is the only required element
        ## "sources" model is the main data model for the VA toolbox database
        new = models.sources(link = this_link, title = this_title, feed_url = feed.url)
          
        ## Add data to the new item's record
        if a.find("description") <> None:
          new.description = a.find("description").text
        try:
          new.date = mdt.rssdateconvert(a.find("pubDate").text)
        except:
          new.date = datetime.now()

        new.tags = feed.for_tags
        new.report = feed.for_report
        new.office = feed.office
        new.posted_by = feed.owner
        new.date_added = datetime.now()

        alc_obj = mat.extract(this_link)
        kws_lookup = find_alternatives("keywords_list", alc_obj.keywords())
        new.keywords = kws_lookup['new_list']
        cpts_lookup = find_alternatives("concepts_list", alc_obj.concepts())
        new.concepts = cpts_lookup['new_list']

        new.content = alc_obj.text()
        ## put the item in the database
        new.put()    
        ## add item to update info return
        update_info[feed.url].append({'link': this_link, 'title': this_title})   
    feed.last_updated = datetime.now()
    feed.put()
  return update_info

  
