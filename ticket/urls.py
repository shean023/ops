# _*_ coding: utf-8 _*_
from django.urls import path, re_path
from ticket import views

urlpatterns = [

    re_path(r'^ticket_manage/$', views.ticket_manage, name="ticket_manage"),
    re_path(r'^ticket_type/$', views.ticket_type, name="ticket_type"),


]
