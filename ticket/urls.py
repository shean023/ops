# _*_ coding: utf-8 _*_
from django.urls import path, re_path
from ticket import views

urlpatterns = [

    re_path(r'^ticket_manage/$', views.ticket_manage, name="ticket_manage"),
    re_path(r'^ticket_create/$', views.ticket_create, name="ticket_create"),
    re_path(r'^ticket_execute/$', views.ticket_execute, name="ticket_execute"),
    re_path(r'^ticket_check/$', views.ticket_check, name="ticket_check"),
    re_path(r'^ticket_mycreate/$', views.ticket_mycreate, name="ticket_mycreate"),
    re_path(r'^ticket_history/$', views.ticket_history, name="ticket_history"),
    re_path(r'^ticket_type/$', views.ticket_type, name="ticket_type"),
    re_path(r'^ticket_edit/(?P<pk>[0-9]+)/$', views.ticket_edit, name="ticket_edit"),
    re_path(r'^ticket_mydel/(?P<pk>[0-9]+)/$', views.ticket_mydel, name="ticket_mydel"),

]
