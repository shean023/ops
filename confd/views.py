import os, etcd3
from django.http import JsonResponse
from django.shortcuts import render
from etcd3.exceptions import ConnectionFailedError

from confd.models import Config_Confd, Confd_Detail
from assets.models import Assets, ServerAssets, ProjectName,ProjectApp,ProjectEnv,PlatformName
from django.contrib.auth.decorators import permission_required
from django.conf import settings


@permission_required('projs.add_project', raise_exception=True)
def confd_list(request):
    confds=Config_Confd.objects.all()
    return render(request, 'confd/confd_list.html', locals())

@permission_required('projs.add_project', raise_exception=True)
def confd_create(request):
    if request.method == 'GET':
        platform_names = PlatformName.objects.all()
        proj_envs = ProjectEnv.objects.all()
        return render(request, 'confd/confd_create.html', locals())
    elif request.method == "POST":
        #print(request.POST.get('asset_projenv'))
        #print(request.POST.get('asset_platform'))
        platform_names = PlatformName.objects.all()
        proj_envs = ProjectEnv.objects.all()
        return render(request, 'confd/confd_create.html', locals())

@permission_required('projs.add_project', raise_exception=True)
def confd_modify(request):
    pk = request.GET.get('id')
    platform_names = PlatformName.objects.all()
    proj_names = ProjectName.objects.all()
    proj_envs = ProjectEnv.objects.all()
    confd = Config_Confd.objects.get(id=pk)
    projapps = ProjectApp.objects.filter(projectname=confd.asset_proj)


    if pk:
        return render(request, 'confd/confd_modify.html', locals())

@permission_required('projs.add_project', raise_exception=True)
def confd_detail(request):
    pk = request.GET.get('id')
    confd = Config_Confd.objects.get(id=pk)
    keys = Confd_Detail.objects.filter(confd_name=confd)
    if pk:
        return render(request, 'confd/confd_detail.html', locals())


@permission_required('projs.add_project', raise_exception=True)
def confd_deploy(request):
    if request.method == 'POST':
        pk = request.POST.get('id')
        try:
            if pk:
                confd = Config_Confd.objects.get(id=pk)
                client = etcd3.client(settings.ETCD_HOST, settings.ETCD_PORT)
                etcd_dir = os.path.join('/' + str(confd.asset_projenv.id), str(confd.asset_platform.id), str(confd.asset_proj.id), str(confd.asset_projapp.id), str(confd.confd_ns))
                keys = Confd_Detail.objects.filter(confd_name=pk)
                for key in keys:
                    if key.confd_deploy_status == 0:
                        client.put_if_not_exists(etcd_dir + "/" + key.confd_key, key.confd_value)
                    else:
                        if key.confd_status == 1 or key.confd_status == 2:
                            client.put(etcd_dir + "/" + key.confd_key, key.confd_value)
                            try:
                                Confd_Detail.objects.filter(id=key.id).update(confd_deploy_status=0, confd_status=0)
                            except Exception as e:
                                return JsonResponse({'code': 500, 'msg': '更新key失败：key: {}, {}'.format(key.confd_key,e)})
                        elif  key.confd_status == 3:
                            client.delete(etcd_dir + "/" + key.confd_key)
                            try:
                                Confd_Detail.objects.filter(id=key.id).update(confd_deploy_status=0)
                            except Exception as e:
                                return JsonResponse({'code': 500, 'msg': '更新key失败：key: {}, {}'.format(key.confd_key,e)})
                return JsonResponse({'code': 200, 'msg': '发布成功！'})
            else:
                return JsonResponse({'code': 500, 'msg': '未获取到ID'})
        except ConnectionFailedError:
            return JsonResponse({'code': 500, 'msg': '获取失败：etcd3无法连接，请联系管理员！'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})