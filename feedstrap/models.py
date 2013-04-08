from django.db import models

class sources(db.Model):
    # for versioning
    date = db.DateTimeProperty()
    date_added = db.DateTimeProperty()
    last_updated = db.DateTimeProperty()
    feed_url = db.StringProperty()

    #Weekly Read Stuff
    office = db.StringProperty()
    title = db.StringProperty()
    link = db.StringProperty(required=True)
    tags = db.ListProperty(str)
    description = db.TextProperty()
    relevance = db.TextProperty()

    #ESIL Stuff
    esil = db.ListProperty(str)

    #Alchemy Stuff
    content = db.TextProperty()
    keywords = db.ListProperty(str)
    concepts = db.ListProperty(str)

    posted_by = db.StringProperty() # AKA Feed Owner


    # Report Selectors
    report = db.ListProperty(str)

    processed = db.BooleanProperty()
    def put(self):
        k = super(sources, self).put()
        create_document(self)
        return k

    def delete(self):
        search.Index(name="sources_docs").delete(str(self.key()))
        k = super(sources, self).delete()
        return k

class blacklist(db.Model):
    link = db.StringProperty(required=True)
    date_deleted = db.DateTimeProperty()

class feeds(db.Model):
    owner = db.StringProperty (required=True)
    office = db.StringProperty (required=True)
    name = db.StringProperty ()
    url = db.StringProperty (required=True)
    for_tags = db.ListProperty(str)
    for_esil = db.ListProperty(str)
    for_report = db.ListProperty(str)
    date_added = db.DateTimeProperty()
    description = db.StringProperty()
    last_updated = db.DateTimeProperty()

class deletedlinks(db.Model):
    link = db.StringProperty (required=True)
    date = db.DateTimeProperty(required=True)

class capabilities(db.Model):
    name = db.StringProperty (required=True)
    code = db.StringProperty (required=True)
    category = db.StringProperty (required=True)

class criteria(db.Model):
    name = db.StringProperty (required=True)
    group = db.StringProperty (required=True)
    area = db.StringProperty (required=True)

class topics(db.Model):
    name = db.StringProperty (required=True)
    description = db.TextProperty()
    options = db.ListProperty(str)
    data_sources = db.ListProperty(str)
    imperatives = db.ListProperty(str)
    capabilities = db.ListProperty(str)

class comments(db.Model):
    name = db.StringProperty (required=True)
    email = db.StringProperty()
    org = db.StringProperty()
    comment = db.TextProperty (required=True)
    date = db.DateTimeProperty(required=True)
    deleted = db.BooleanProperty()

class selectors(db.Model):
    phrases_list = db.ListProperty(str)
    values = db.ListProperty(int)
    name = db.StringProperty (required=True)

class my_errors(db.Model):
    description = db.StringProperty (required=True)
    date = db.DateTimeProperty(required=True)

class search_log(db.Model):
    search_term = db.StringProperty (required=True)
    date = db.DateTimeProperty(required=True)
    referal = db.StringProperty()
    user = db.StringProperty()

class clicks(db.Model):
    link = db.StringProperty (required=True)
    date = db.DateTimeProperty(required=True)
    referal = db.StringProperty()
    user = db.StringProperty()


class alt_names(db.Model):
    field = db.StringProperty (required=True)
    name = db.StringProperty (required=True)
    alternatives = db.ListProperty(str)
