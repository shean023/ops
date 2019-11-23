# -*- coding: utf-8 -*-

from django.urls import path, re_path
from assets import views, gateone, winremote

urlpatterns = [
    path(r'proj_list/', views.proj_list, name='proj_list'),
    path(r'assets_charts/', views.get_assets_charts, name='assets_charts'),
    path(r'assets_list/', views.get_assets_list, name='assets_list'),
    path(r'update_pwd/', views.update_pwd, name='update_pwd'),
    path(r'add_asset/', views.add_asset, name='add_asset'),
    path(r'add_base_asset/', views.add_base_asset, name='add_base_asset'),
    re_path(r'update_asset/(?P<asset_type>(.*?))/(?P<pk>[0-9]+)/', views.update_asset, name='update_asset'),
    path(r'server_facts/', views.server_facts, name='server_facts'),
    re_path(r'get_server_info/(?P<pk>[0-9]+)/', views.get_asset_info, name='get_asset_info'),
    path(r'import_assets/', views.import_assets, name='import_assets'),
    re_path(r'export_assets/', views.export_assets, name='export_assets'),
    re_path(r'ssh/(?P<pk>[0-9]+)/', views.ssh_terminal, name='ssh_terminal'),
    re_path(r'guacamole/(?P<pk>[0-9]+)/', views.guacamole_terminal, name='guacamole_terminal'),
    path(r'login_record/', views.login_record, name='login_record'),
    re_path(r'admin_play/(?P<pk>[0-9]+)/', views.admin_play, name='admin_play'),
    #re_path(r'^remote/(?P<sid>[0-9]+)/$', winremote.index, name='index'),
    re_path(r'gateone/(?P<aid>[0-9]+)/$', gateone.gateone),
    re_path(r'gateone/auth/$', gateone.get_auth_obj),
]
