from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'feedstrap.home.MainPage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'rss', 'feedstrap.rss.main'),
    url(r'weeklyreads/(?P<site>.+)/', 'feedstrap.reports.weeklyreads'),
    url(r'weeklyreads', 'feedstrap.reports.weeklyreads'),
    url(r'csv', 'feedstrap.reports.export_csv'),
    url(r'esil/(?P<site>.+)/', 'feedstrap.reports.esil'),
    url(r'esil', 'feedstrap.reports.esil'),
    url(r'^edit/resource/', 'feedstrap.edit.main'),
    url(r'^add_new', 'feedstrap.edit.add_new'),
    url(r'^q/(?P<template>.+)/', 'feedstrap.home.MainPage'),
    url(r'^q', 'feedstrap.home.MainPage'),
    url(r'^account/edit', 'feedstrap.user.main'),
    url(r'^account/change_password', 'feedstrap.user.psw'),
    url(r'^account/info', 'feedstrap.user.info'),
    url(r'^signin', 'feedstrap.user.signin'),
    url(r'^signout', 'feedstrap.user.signout'),
    url(r'^filter', 'feedstrap.filter.main'),
    url(r'(?P<static_page>.+)', 'feedstrap.home.StaticPage'),
)
