#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:

from . import cguacamole
from django.conf import settings
from django.shortcuts import render

from django.contrib.auth.decorators import permission_required, login_required
import uuid


@login_required(login_url='/login')
@permission_required('OpsManage.can_read_deploy_record',login_url='/noperm/')
def index(request, sid):

    ADMIN_USERNAME = settings.ADMIN_USERNAME
    ADMIN_PASSWORD = settings.ADMIN_PASSWORD
    GUACAMOLE_HOST = settings.GUACAMOLE_HOST
    GUACAMOLE_PORT = settings.GUACAMOLE_PORT
    GUACAMOLE_SERVER_PATH = settings.GUACAMOLE_SERVER_PATH

    try:
        host_name = Server_Assets.objects.filter(id=sid)[0].hostname
        env_name = Env_Msg.objects.filter(id=Server_Assets.objects.filter(id=sid)[0].envmsg)[0].env_name
        server_ip = Server_Assets.objects.filter(id=sid)[0].ip
        server_port = Server_Assets.objects.filter(id=sid)[0].port
        server_username = Server_Assets.objects.filter(id=sid)[0].username
        server_password = Server_Assets.objects.filter(id=sid)[0].passwd
        server_system = Server_Assets.objects.filter(id=sid)[0].system
        server_pt = Project_Assets.objects.filter(id=(Assets.objects.filter(id=Server_Assets.objects.filter(id=sid)[0].assets_id)[0].project))[0].project_name

    except BaseException as e:
        print(e.message)
        return render(request, 'core/error.html', {})

    else:
        try:
            if request.user.is_superuser:
                pass
            else:
                user_server = User_Server.objects.get(user_id=request.user.id, server_id=sid)
                if user_server:
                    pass
                else:
                    return render(request, 'core/error.html', {"errorinfo": "请联系管理员"})

        except BaseException as e:
            return render(request, 'core/error.html', {"errorinfo": "请联系管理员"})

        username = "%s" %(request.user)
        password = str(uuid.uuid4)
        remote_ip = server_ip
        remote_port = server_port
        remote_host_username = server_username
        remote_host_password = server_password
        remote_host_system = server_system
        performance = 0  # 0-5 (桌面、主题、ClearType、Aero、菜单动画、声音、麦克风、打印机)
        connection_name = server_pt + "_" + env_name + "_" + host_name + "_" + remote_ip

        client = cguacamole.Client(ADMIN_USERNAME, ADMIN_PASSWORD, GUACAMOLE_HOST, GUACAMOLE_PORT, GUACAMOLE_SERVER_PATH)

        if client.login() is not None:
            # Delete user, group named username ,connections belong the group(Last connection coulden't delete auto).
            #guacamole.delete_user_all_residuals(client, username)

            # Delete connection named connection_name (For connection created in 'ROOT' group).
            #guacamole.delete_connections(client, connection_name)

            # Delete the connection belong the user.
            #client.delete_connection(client.get_user_connection_id(username, connection_name))

            if remote_host_system < 10:

                rdp_url = cguacamole.create_user_connection(client, username=username, password=password,
                                                            remote_ip=remote_ip,
                                                            host_username=remote_host_username,
                                                            host_password=remote_host_password,
                                                            host_port=remote_port,
                                                            performance=performance,
                                                            connection_name=connection_name,
                                                            connection_type='rdp',
                                                            private_key='',
                                                            command='',
                                                            only_one=True)
                #print(rdp_url)

            elif remote_host_system >= 10:
                ssh_url = cguacamole.create_user_connection(client, username=username, password=password,
                                                            remote_ip=remote_ip,
                                                            host_username='',
                                                            host_password='',
                                                            host_port=remote_port,
                                                            performance=performance,
                                                            connection_name=connection_name,
                                                            connection_type='ssh',
                                                            private_key='',
                                                            command='',
                                                            only_one=True)
                #print(ssh_url)

            else:
                pass

        client.logout()

        client1 = cguacamole.Client(username, password, GUACAMOLE_HOST, GUACAMOLE_PORT, GUACAMOLE_SERVER_PATH)
        return render(request, 'core/remote.html',
                      {"user": request.user, "hostname": host_name,
                       "envname": env_name, "serverip": server_ip,
                       "serverport": server_port, "connecturl": client1.login})

