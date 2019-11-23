#!/usr/bin/env python
# _#_ coding:utf-8 _*_

import logging
from django.http import JsonResponse
import time, hmac, hashlib
from django.shortcuts import render
from assets.models import *
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.conf import settings


def create_signature(secret, *parts):
    hash = hmac.new(secret, digestmod=hashlib.sha1)
    for part in parts:
        hash.update(str(part).encode("utf-8"))
    return hash.hexdigest()


#@login_required(login_url='/login')
#@permission_required('assets.add_assets', raise_exception=True)
def get_auth_obj(request):

    api_key = settings.GATEONE_API_KEY
    secret = settings.GATEONE_API_SECRET
    gateone_url = settings.GATEONE_SERVER_ADDR
    user = str(request.user)
    authobj = {
        'api_key': api_key,
        'upn': user,
        'timestamp': str(int(time.time() * 1000)),
        'signature_method': 'HMAC-SHA1',
        'api_version': '1.0',
    }

    authobj['signature'] = create_signature(secret, authobj['api_key'], authobj['upn'], authobj['timestamp'])
    auth_info_and_server = {'url': gateone_url , 'auth': authobj }
    return JsonResponse(auth_info_and_server)


@login_required(login_url='/login')
@permission_required('assets.add_assets', raise_exception=True)
def gateone(request,aid):
    try:
        asset = Assets.objects.get(id=aid)
        if request.user.is_superuser:
            return render(request,'assets/gateone.html',{"user":request.user,"asset": asset})
        else:
            # user_server = User_Server.objects.get(user_id=request.user.id, server_id=aid)
            # userServer = User_Server.objects.filter(user_id=request.user.id)
            # serverList = []
            # for s in userServer:
            #     ser = Server_Assets.objects.get(id=s.server_id)
            #     serverList.append(ser)
            # if user_server:
            #     return render(request,'webssh/gateone.html',{"user":request.user,"server":server})
            pass
    except Exception as ex:
        logging.getLogger().error(msg="请求gateone失败: {ex}".format(ex=str(ex)))
        return render(request,'assets/gateone.html',{"user":request.user,"errorInfo":"请联系管理员"})

