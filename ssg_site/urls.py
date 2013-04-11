from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
   (r'^dbedit', 'feedstrap.home.dbedit'),
   (r'^$', 'feedstrap.home.MainPage'),
    url(r'^admin/', include(admin.site.urls)),
)