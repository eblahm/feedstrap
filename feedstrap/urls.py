from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'feedstrap.home.MainPage'),
    url(r'esil', 'feedstrap.esil.main'),
    url(r'esil/(?P<site>.+)/', 'feedstrap.esil.main'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^edit/resource/', 'feedstrap.home.dbedit'),
    url(r'^q/(?P<template>.+)/', 'feedstrap.home.MainPage'),
    url(r'^q', 'feedstrap.home.MainPage'),
    # url(r'^read', 'feedstrap.home.read'),
    url(r'^filter', 'feedstrap.filter.main'),
)
