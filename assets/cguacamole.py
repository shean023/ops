#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:

import requests
import json
import logging
import base64
#import uuid

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class User(object):
    def list_user(self):
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'users' + self.token])
        return json.loads(requests.get(url=url, params={'token': self.token},
                                       headers={'Content-Type': 'application/json;charset=UTF-8'}).text)

    def create_user(self, username, password):
        data = {"username": username,
                "password": password,
                "attributes": {
                    "disabled": "",
                    "expired": "",
                    "access-window-start": "",
                    "access-window-end": "",
                    "valid-from": "",
                    "valid-until": "",
                    "timezone": None}
                }
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'users'])
        return json.loads(requests.post(url=url, json=data, params={'token': self.token},
                                        headers={'Content-Type': 'application/json;charset=UTF-8'}).text)

    def update_user(self, username, new_password, new_username=''):
        if new_username == '':
            new_username = username
        data = {"username": new_username,
                "password": new_password,
                "attributes": {
                    "disabled": "",
                    "expired": "",
                    "access-window-start": "",
                    "access-window-end": "",
                    "valid-from": "",
                    "valid-until": "",
                    "timezone": None}
                }
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'users', username])
        return requests.put(url=url, json=data, params={'token': self.token},
                            headers={'Content-Type': 'application/json;charset=UTF-8'}).text

    def delete_user(self, username):
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'users', username])
        return requests.delete(url=url, params={'token': self.token}).text

    def permissions(self, username, connection_id, connection_group_id):
        data = [
            {
                "op": "add",
                "path": r"/connectionPermissions/" + str(connection_id),
                "value": "READ"
            },
        ]
        if connection_group_id != 'ROOT':
            data.append({
                "op": "add",
                "path": r"/connectionGroupPermissions/" + str(connection_group_id),
                "value": "READ"
            })
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'users', username, 'permissions'])
        return requests.patch(url=url, json=data, params={'token': self.token},
                              headers={'Content-Type': 'application/json;charset=UTF-8'}).text

    def get_user_info(self, username, password):
        _client = Client(username, password, self.host, self.port, self.server_path)
        _client.login()
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'connectionGroups', 'ROOT', 'tree'])
        return json.loads(requests.get(url=url, params={'token': _client.token}).text)

    def get_user_group_id(self, username):
        try:
            info = self.get_user_info(self.username, self.password)['childConnectionGroups']
            for group in info:
                if group.get('name', '') == username:
                    return group.get('identifier', None)
        except KeyError:
            log.warning('ConnectionGroups list empty, ')
            # raise KeyError('ConnectionGroupsListEmpty')

    def get_user_connection_id(self, username, connection_name=''):
        if connection_name == '':
            connection_name = username
        try:
            info = self.get_user_info(self.username, self.password)['childConnectionGroups']
            for group in info:
                if group.get('name', 'ROOT') == username:
                    for connection in group.get('childConnections', [{}]):
                        if connection.get('name', '') == connection_name:
                            return connection.get('identifier', None)
        except KeyError:
            log.warning('ConnectionGroups list empty')
            # raise KeyError('ConnectionGroupsListEmpty')

    def get_connections_id(self, connection_name):
        # TODO Deep 2 now, more
        connections_id = []
        try:
            info = self.get_user_info(self.username, self.password)
            for group in info.get('childConnectionGroups', [{}]):
                for connection in group.get('childConnections', [{}]):
                    if connection.get('name', '') == connection_name:
                        connections_id.append(connection.get('identifier', None))
            for connection in info.get('childConnections', [{}]):
                if connection.get('name', '') == connection_name:
                    connections_id.append(connection.get('identifier', None))
        except KeyError:
            log.warning('ConnectionGroups list empty')
            # raise KeyError('ConnectionGroupsListEmpty')
        return connections_id

    def get_user_permissions(self, username):
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'users', username, 'permissions'])
        return json.loads(requests.get(url=url, params={'token': self.token}).text)


class ConnectionGroup(object):
    def create_connection_group(self, name):
        data = {
            "parentIdentifier": "ROOT",
            "name": name,
            "type": "ORGANIZATIONAL",
            "attributes": {
                "max-connections": "1",
                "max-connections-per-user": "1",
                "enable-session-affinity": "false"
            }
        }
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'connectionGroups'])
        return json.loads(requests.post(url=url, json=data, params={'token': self.token},
                                        headers={'Content-Type': 'application/json;charset=UTF-8'}).text)

    def delete_connection_group(self, connection_group_id):
        url = '/'.join([self.base_api_url, 'session', 'data',
                        self.data_sources, 'connectionGroups', str(connection_group_id)])
        return requests.delete(url=url, params={'token': self.token}).text


class Connection(object):
    def get_active_connections(self):
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'activeConnections'])
        return json.loads(requests.get(url=url, params={'token': self.token}).text)

    def kill_active_connection(self, identifier):
        data = [{
            "op": "remove", "path": ''.join(["/", identifier])
        }]
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'activeConnections'])
        return requests.patch(url=url, json=data, params={'token': self.token},
                              headers={'Content-Type': 'application/json;charset=UTF-8'}).text

    def kill_user_active_connections(self, username):
        data = {}
        for k, v in self.get_active_connections().items():
            if v.get('username') == username:
                data[k] = self.kill_active_connection(v.get('identifier'))
        return data

    def create_rdp_connection(self, name, hostname, username, password, hostport, parent_identifier='ROOT', performance=False,):
        data = {
            "parentIdentifier": str(parent_identifier),
            "name": name,
            "protocol": 'rdp',
            "parameters": {
                "port": '%s' % hostport,
                "read-only": "",
                "swap-red-blue": "",
                "cursor": "",
                "color-depth": "",
                "clipboard-encoding": "",
                "dest-port": "",
                "recording-path": "/opt/rdprecord/${GUAC_USERNAME}",
                "create-recording-path": "true",
                "recording-name": "%s_${GUAC_DATE}_${GUAC_TIME}" %(name),
                "enable-sftp": "",
                "sftp-port": "",
                "enable-audio": "true" if performance > 4 else "",
                "security": "",
                "disable-auth": "",
                "ignore-cert": "",
                "server-layout": "",
                "console": "",
                "width": "",
                "height": "",
                "dpi": "",
                "resize-method": "",
                "console-audio": "",
                "disable-audio": "",
                "enable-audio-input": "true" if performance > 4 else "",
                "enable-printing": "true" if performance > 4 else "",
                "enable-drive": "true",
                "create-drive-path": "true",
                "drive-path":"/opt/drive_path/${GUAC_USERNAME}",
                "enable-wallpaper": "true" if performance > 0 else "",
                "enable-theming": "true" if performance > 1 else "",
                "enable-font-smoothing": "true" if performance > 2 else "",  # (ClearType)
                "enable-full-window-drag": "true" if performance > 2 else "",
                "enable-desktop-composition": "true" if performance > 3 else "",  # (Aero)
                "enable-menu-animations": "true" if performance > 3 else "",
                "preconnection-id": "",
                "hostname": hostname,
                "username": username,
                "password": password
            },
            "attributes": {
                "max-connections": "5",
                "max-connections-per-user": "10"
            }
        }
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'connections'])
        return json.loads(requests.post(url=url, json=data, params={'token': self.token},
                                        headers={'Content-Type': 'application/json;charset=UTF-8'}).text)

    def create_ssh_connection(self, name, hostname, hostport, private_key, command, parent_identifier='ROOT'):
        print("private_key:")
        print(private_key)
        data = {
            "parentIdentifier": str(parent_identifier),
            "name": name,
            "protocol": 'ssh',
            "parameters": {
                "port": '%s' % hostport,
                "read-only": "",
                "clipboard-encoding": "",
                "recording-path": "/opt/sshrecord/${GUAC_USERNAME}",
                "create-recording-path": "true",
                "recording-name": "%s_${GUAC_DATE}_${GUAC_TIME}" %(name),
                "color-scheme": 'white-black',
                "enable-sftp": "true",
                "sftp-root-directory": "/home/${GUAC_USERNAME}",
                "hostname": hostname,
                "username": '${GUAC_USERNAME}',
                "password": '',
                "private-key": '%s' %(private_key),
                "command": command
            },
            "attributes": {
                "max-connections": "10",
                "max-connections-per-user": "10"
            }
        }
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'connections'])
        return json.loads(requests.post(url=url, json=data, params={'token': self.token},
                                        headers={'Content-Type': 'application/json;charset=UTF-8'}).text)

    def delete_connection(self, connection_id):
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'connections', str(connection_id)])
        return requests.delete(url=url, params={'token': self.token}).text

    def get_connection_info(self, connection_id):
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'connections', str(connection_id)])
        return json.loads(requests.get(url=url, params={'token': self.token}).text)

    def can_connect(self, connection_id):
        info = self.get_connection_info(connection_id)
        if info.get('message', None):
            log.error(info.get('message'))
            return False
        else:
            return True


class Client(User, ConnectionGroup, Connection):
    def __init__(self, username, password, host='10.32.100.16', port=8080, server_path=''):
        super(Client, self).__init__()
        self.CONNECTION_TYPE = {
            'connection': 'c'
        }
        self.username = username
        self.password = password
        self.token = ''
        self.available_data_sources = ''
        self.data_sources = ''
        self.host = host
        self.port = port
        self.server_path = server_path
        self.base_url = ''.join([r'http://', '/'.join([':'.join([host, str(self.port)]), server_path, '#'])])
        self.base_api_url = ''.join([r'http://', '/'.join([':'.join([host, str(self.port)]), server_path, 'api'])])
        # self.login()

    # def __del__(self):
    #     if self.token is not '':
    #         self.logout()
    #     for method in [getattr(Client, e) for e in dir(Client) if '__' not in e]:
    #         del method
    #     print(self.__class__.login)

    def login(self):
        data = {
            "username": self.username,
            "password": self.password,
        }
        try:
            res = json.loads(requests.post(url='/'.join([self.base_api_url, 'tokens']), data=data,
                                           headers={'Content-Type': 'application/x-www-form-urlencoded'}).text)
        except:
            log.warning('guacamole client connection failed')
            return None
        try:
            self.token = res['authToken']
            self.available_data_sources = res['availableDataSources']
            self.data_sources = res['dataSource']
            return self.token
        except KeyError:
            log.warning('username:%s login failed' % self.username)
            return None
            # self.__del__()

    def logout(self, force=True):
        if force:
            self.login()
        return requests.delete(url='/'.join([self.base_api_url, 'tokens', self.token])).text

    def info(self):
        url = '/'.join([self.base_api_url, 'session', 'data', self.data_sources, 'connectionGroups', 'ROOT', 'tree'])
        return json.loads(requests.get(url=url, params={'token': self.token}).text)

    def get_connection_url(self, connection_id, connection_type):
        path = b'\x00'.join([str(connection_id).encode(),
                             self.CONNECTION_TYPE.get(connection_type, 'c').encode(),
                             self.data_sources.encode()])
        return ''.join(['/'.join([self.base_url, 'client', base64.b64encode(path).decode()]), '?token=', self.token])


def create_user_connection(client, username, password, remote_ip, host_username, host_password, host_port,
                           performance=0, connection_name='', connection_type='rdp', private_key='', command='', only_one=True):
    if client.create_user(username, password).get('type', '') == 'BAD_REQUEST':
        client.update_user(username, password)
        # log.warning('用户存在,已更新用户密码')
    if connection_name == '':
        connection_name = username

    if only_one:
        new_group_id = "ROOT"
    else:
        res = client.create_connection_group(username)
        new_group_id = res.get('identifier', None) or client.get_user_group_id(username) or "ROOT"

    if connection_type == 'rdp':
        res = client.create_rdp_connection(name=connection_name, hostname=remote_ip, username=host_username,
                                           password=host_password, hostport=host_port, parent_identifier=new_group_id,
                                           performance=performance)
    elif connection_type == 'ssh':
        res = client.create_ssh_connection(name=connection_name, hostname=remote_ip, hostport=host_port, command=command,
                                           private_key=private_key, parent_identifier=new_group_id)
    else:
        pass

    if res.get('message', None):
        log.error(res['message'])

        User.permissions(client, username, client.get_connections_id(connection_name)[0], 'ROOT')
        log.info('Give %s Add Permissions Is Remote_HOST_ID: %s ' % (username, client.get_connections_id(connection_name)[0]))

    else:
        new_connection_id = res.get('identifier', None) or client.get_user_connection_id(connection_name)
        print(new_connection_id)
        print(client.get_user_connection_id(connection_name))
        log.info('New connection id:%s' % new_connection_id)

        if new_connection_id:
            client.permissions(username=username, connection_id=new_connection_id, connection_group_id=new_group_id)
            user_client = Client(username, password, client.host, client.port, client.server_path)
            if user_client.login() and user_client.can_connect(new_connection_id):
                return user_client.get_connection_url(new_connection_id, 'connection')


def delete_user_all_residuals(client, username):
    # Client(username, password, client.host, client.port, client.server_path).logout()
    client.kill_user_active_connections(username)

    connection_id = client.get_user_connection_id(username)
    if connection_id:
        client.delete_connection(connection_id)

    connection_group_id = client.get_user_group_id(username)
    if connection_group_id:
        client.delete_connection_group(connection_group_id)

    client.delete_user(username)


def delete_connections(client, connection_name):
    for _id in client.get_connections_id(connection_name):
        client.delete_connection(_id)
        log.info('Connection id:%s has been delete' % _id)

