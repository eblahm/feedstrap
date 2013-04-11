from django.conf.urls import patterns, url

from feedstrap import home #, ssg_app, sharepoint

urlpatterns = patterns('',
                       (r'^dbedit', 'feedstrap.home.dbedit'),
                       (r'^$', 'feedstrap.home.MainPage'),
)


# urlpatterns = patterns('',
# #     url('/db_save', home.db_save_click),
# #     url('/search', home.MainPage),
# #     url('/advanced_search', home.AdvancedSearch),
# #     url('/trends', ssg_app.TrendsHandler1),
# #     url('/pir_breakout', ssg_app.TrendsHandler2),
# #     url('/esil', sharepoint.ESILHandler),
# #     url('/esil/url(.+)', sharepoint.ESIL_Extend_Handler),
# #     url('/search', home.MainPage),
# #     url('/ajax/url(.+)', home.AjaxHandler),
# #     url('/bulk_post', home.AjaxHandler),
# #     url('/remap_fields', home.NewFieldsHandler),
# )