from django.conf.urls import patterns, include, url
from django.contrib import admin
from feedstrap import handle_main
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'feedstrap.home.MainPage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^db/', include(handle_main)),
)