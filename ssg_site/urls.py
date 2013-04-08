from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ssg_site.views.home', name='home'),
    # url(r'^ssg_site/', include('ssg_site.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

)

# ([('/db_edit', home.db_edit_click),
#   ('/db_save', home.db_save_click),
#   ('/search', home.MainPage),
#   ('/advanced_search', home.AdvancedSearch),
#   ('/trends', ssg_app.TrendsHandler1),
#   ('/pir_breakout', ssg_app.TrendsHandler2),
#   ('/esil', sharepoint.ESILHandler),
#   ('/esil/(.+)', sharepoint.ESIL_Extend_Handler),
#   ('/search', home.MainPage),
#   ('/ajax/(.+)', home.AjaxHandler),
#   ('/bulk_post', home.AjaxHandler),
#   ('/remap_fields', home.NewFieldsHandler),
#   ('/', home.MainPage),], debug=True)