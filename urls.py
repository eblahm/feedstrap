from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'feedstrap.home.MainPage'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'rss', 'feedstrap.rss.main'),
    url(r'weeklyreads', 'feedstrap.reports.weeklyreads'),
    url(r'csv', 'feedstrap.reports.export_csv'),
    url(r'esil/comments/post/', 'feedstrap.reports.comment_handler'),
    url(r'^comments/', include('django_comments_xtd.urls')),
    url(r'esil/comment/delete/(?P<comment_id>.+)', 'feedstrap.reports.delete_comment'),
    url(r'esil/(?P<pk>.+)/comments', 'feedstrap.reports.all_comments'),
    url(r'esil/(?P<pk>.+)/', 'feedstrap.reports.single_topic'),
    url(r'esil', 'feedstrap.reports.all_topics'),
    url(r'^edit/resource/delete', 'feedstrap.edit.delete'),
    url(r'^edit/resource/', 'feedstrap.edit.main'),
    url(r'^add_new', 'feedstrap.edit.add_new'),
    url(r'^q/(?P<template>.+)/', 'feedstrap.home.MainPage'),
    url(r'^q', 'feedstrap.home.MainPage'),
    url(r'^account/edit', 'feedstrap.user.main'),
    url(r'^account/change_password', 'feedstrap.user.psw'),
    url(r'^account/info', 'feedstrap.user.info'),
    url(r'^signup/(?P<secret>.+)', 'feedstrap.user.signup'),
    url(r'^signin', 'feedstrap.user.signin'),
    url(r'^signout', 'feedstrap.user.signout'),
    url(r'^data/(?P<model>.+)', 'feedstrap.filter.data'),
    url(r'^filter/link/(?P<action>.*)', 'feedstrap.edit.edit_link'),
    url(r'^invite/(?P<action>.*)/', 'feedstrap.user.invite'),
    url(r'(?P<static_page>.+)', 'feedstrap.home.StaticPage'),
)