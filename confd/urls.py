# _*_ coding: utf-8 _*_
from django.urls import path, re_path
from confd import views

urlpatterns = [

    re_path(r'^confd_list/$', views.confd_list, name="confd_list"),
    re_path(r'^confd_modify/$', views.confd_modify, name="confd_modify"),
    re_path(r'^confd_create/$', views.confd_create, name="confd_create"),
    re_path(r'^confd_detail/$', views.confd_detail, name="confd_detail"),
    re_path(r'^confd_deploy/$', views.confd_deploy, name="confd_deploy"),

]
