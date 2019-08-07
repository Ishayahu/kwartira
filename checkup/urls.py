# -*- coding: utf-8 -*-
from django.conf.urls import url
from checkup.views import *

urlpatterns = [
    # ex: /polls/


    url(r'^$', index, name='index'),
    # url(r'^faq/(?P<language_code>[a-zA-Z_]+)/$', filebased.file_edit, {'filename': 'faq'}, name='faq'),
    url(r'^visit/add/$', visit_add,name='visit_add'),
    url(r'^visit/show/(?P<visit_id>\d+)/$', visit_show_by_id,name='visit_show_by_id'),
    url(r'^visit/show/for_date/(?P<date>\d{4}-\d{2}-\d{2})/$', visit_show_by_date, name='visit_show_by_date'),
    url(r'^visit/show/last/(?P<count>\d+)/for_user/(?P<user_id>\d+)/$', visit_show_for_user, name='visit_show_for_user'),
    url(r'^visit/show/28last/for_user/(?P<user_id>\d+)/$', visit_show_for_user, name='visit_show_default_for_user', kwargs={'count': 28}),
    # url(r'^feedback/(?P<feedback_id>\d+)/delete/$', feedback.delete, name='feedback-delete'),
    #
    # # API
    # url(r'^api/faq/(?P<language_code>[a-zA-Z_]+)/get/$', api.file_get, {'filename': 'faq'}, name='api-faq-get'),
    # url(r'^api/feedback/file/(?P<user_id>\d+)/post/$', api.save_file_feedback, name='api-save_file_feedback'),
]