import os
import datetime
from ast import literal_eval
from django.shortcuts import render
from django.http import JsonResponse
import time
from projs.models import *
from django.contrib.auth.models import Group
from users.models import UserProfile
from assets.models import Assets, ServerAssets, ProjectName,ProjectApp,ProjectEnv
from utils.decorators import admin_auth, deploy_auth
from projs.utils.git_tools import GitTools
from projs.utils.svn_tools import SVNTools
from django.contrib.auth.decorators import permission_required


@permission_required('projs.add_project', raise_exception=True)
def proj_list(request):
    projects = Project.objects.select_related('project_admin').all()
    project_envs = Project.project_envs
    project_users = UserProfile.objects.all()
    return render(request, 'projs/proj_list.html', locals())


@permission_required('projs.add_service', raise_exception=True)
def proj_org(request, pk):
    project_obj = ProjectName.objects.get(id=pk)
    services = Service.objects.select_related('project').all()
    assets = Assets.objects.filter(asset_proj=project_obj)
    if request.method == 'GET':
        project_org = project_obj.projname_org
        return render(request, 'projs/proj_org.html', locals())
    elif request.method == 'POST':
        try:
            data = request.POST.get('data')
            project_obj.projname_org = data
            project_obj.save()
            return JsonResponse({'code': 200, 'msg': '保存成功！'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '保存失败！{}'.format(e)})


@permission_required('projs.add_service', raise_exception=True)
def org_chart(request, pk):
    project_obj = ProjectName.objects.get(id=pk)
    project_org = project_obj.projname_org
    return render(request, 'projs/org_chart.html', locals())


@admin_auth
def proj_config(request):
    projnames = ProjectName.objects.all()
    projenvs = ProjectEnv.objects.all()
    groupList =  Group.objects.all()
    roleList = ProjectConfig.objects.all()
    repos = ProjectConfig.project_models
    pk = request.GET.get('id')

    if pk:
        return render(request, 'projs/config_detail.html', locals())
    else:
        return render(request, 'projs/proj_config.html', locals())

@admin_auth
def proj_ticket(request):
    pk = request.GET.get('id')
    projnames = ProjectName.objects.all()
    projenvs = ProjectEnv.objects.all()
    groupList =  Group.objects.all()
    roleList = ProjectConfig.objects.all()
    proj_ticket = Project_Config_Ticket.objects.get(id=pk)
    projapps = ProjectApp.objects.filter(projectname=proj_ticket.proj_name)


    if pk:
        return render(request, 'projs/ticket_detail.html', locals())



@permission_required('projs.deploy_project', raise_exception=True)
def config_list(request):
    user = request.user
    configs = ProjectConfig.objects.all
    projnames = ProjectName.objects.all()
    projenvs = ProjectEnv.objects.all()
    groupList = Group.objects.all()
    proj_Tickets = Project_Config_Ticket.objects.all()
    return render(request, 'projs/config_list.html', locals())


@permission_required('projs.deploy_project', raise_exception=True)
def read_branch(request, pk):
    config = ProjectConfig.objects.get(id=pk)
    if request.method == 'GET':
        key = request.GET.get('key', None)
        mode = request.GET.get('mode', 'deploy')
        env = request.GET.get('env','noenv')
        if config.repo == 'git':
            git_tool = GitTools(repo_url=config.repo_url, path=config.src_dir, env=env)
            if key:
                if key == 'model':
                    try:
                        git_tool.clone(prev_cmds=config.prev_deploy)
                        if config.repo_model == 'branch':
                            branches = git_tool.remote_branches
                            return JsonResponse({'code': 200, 'models': branches, 'msg': '获取成功！'})
                        elif config.repo_model == 'tag':
                            tags = git_tool.tags(versions=config.versions.split(','), mode=mode)
                            return JsonResponse({'code': 200, 'models': tags, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
                elif key == 'commit':
                    try:
                        branch = request.GET.get('branch')
                        mode = request.GET.get('mode')
                        if request.GET.get('new_commit'):
                            git_tool.pull(branch)
                        commits = git_tool.get_commits(branch, versions=config.versions.split(','), mode=mode,
                                                       max_count=20)
                        return JsonResponse({'code': 200, 'data': commits, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
            else:
                if os.path.exists(git_tool.proj_path):
                    local_branches = git_tool.local_branches
                    local_tags = tags = git_tool.tags(versions=config.versions.split(','), mode=mode)
                return render(request, 'projs/deploy.html', locals())

        elif config.repo == 'svn':
            svn_tool = SVNTools(repo_url=config.repo_url, path=config.src_dir, env=config.project.project_env,
                                username=config.repo_user, password=config.repo_password)
            if key:
                if key == 'model':
                    try:
                        if config.repo_model == 'branch':
                            branches = svn_tool.branches
                            return JsonResponse({'code': 200, 'models': branches, 'msg': '获取成功！'})
                        elif config.repo_model == 'tag':
                            tags = svn_tool.tags(versions=config.versions.split(','), mode=mode)
                            return JsonResponse({'code': 200, 'models': tags, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
                elif key == 'commit':
                    branch = request.GET.get('branch')
                    try:
                        if branch == 'trunk':
                            commits = svn_tool.get_commits(versions=config.versions.split(','), mode=mode, limit=30)
                        else:
                            commits = svn_tool.get_commits(versions=config.versions.split(','), repo_model='branch',
                                                           model_name=branch, mode=mode, limit=30)
                        return JsonResponse({'code': 200, 'data': commits, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
            else:
                return render(request, 'projs/deploy.html', locals())


#@deploy_auth
def deploy(request, pk):
    config = Project_Config_Ticket.objects.get(id=pk)

    if request.method == 'GET':
        key = request.GET.get('key', None)
        mode = request.GET.get('mode', 'deploy')

        if config.proj_role.repo == 'git':
            git_tool = GitTools(repo_url=config.proj_role.repo_url, path=config.proj_role.src_dir,env='test')
            if key:
                if key == 'model':
                    try:
                        git_tool.clone(prev_cmds=config.proj_role.prev_deploy)
                        if config.proj_role.repo_model == 'branch':
                            branches = git_tool.remote_branches
                            return JsonResponse({'code': 200, 'models': branches, 'msg': '获取成功！'})
                        elif config.proj_role.repo_model == 'tag':
                            tags = git_tool.tags(versions=config.versions.split(','), mode=mode)
                            return JsonResponse({'code': 200, 'models': tags, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
                elif key == 'commit':
                    try:
                        branch = request.GET.get('branch')
                        mode = request.GET.get('mode')
                        if request.GET.get('new_commit'):
                            git_tool.pull(branch)
                        commits = git_tool.get_commits(branch, versions=config.proj_role.versions.split(','), mode=mode,
                                                       max_count=20)
                        return JsonResponse({'code': 200, 'data': commits, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
            else:
                if os.path.exists(git_tool.proj_path):
                    local_branches = git_tool.local_branches
                    local_tags = tags = git_tool.tags(versions=config.proj_role.versions.split(','), mode=mode)

                return render(request, 'projs/deploy.html', locals())

        elif config.repo == 'svn':
            svn_tool = SVNTools(repo_url=config.repo_url, path=config.src_dir, env=config.project.project_env,
                                username=config.repo_user, password=config.repo_password)
            if key:
                if key == 'model':
                    try:
                        if config.repo_model == 'branch':
                            branches = svn_tool.branches
                            return JsonResponse({'code': 200, 'models': branches, 'msg': '获取成功！'})
                        elif config.repo_model == 'tag':
                            tags = svn_tool.tags(versions=config.versions.split(','), mode=mode)
                            return JsonResponse({'code': 200, 'models': tags, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
                elif key == 'commit':
                    branch = request.GET.get('branch')
                    try:
                        if branch == 'trunk':
                            commits = svn_tool.get_commits(versions=config.versions.split(','), mode=mode, limit=30)
                        else:
                            commits = svn_tool.get_commits(versions=config.versions.split(','), repo_model='branch',
                                                           model_name=branch, mode=mode, limit=30)
                        return JsonResponse({'code': 200, 'data': commits, 'msg': '获取成功！'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '获取失败：{}'.format(e)})
            else:
                return render(request, 'projs/deploy.html', locals())

#@deploy_auth
def deploy_apply(request, pk):

    ticket = Project_Config_Ticket.objects.get(id=pk)
    if request.method == 'GET':
        mode = request.GET.get('mode', 'deploy')
        projnames = ProjectName.objects.all()
        projenvs = ProjectEnv.objects.all()
        groupList = Group.objects.all()
        audit_group = Group.objects.get(id=ticket.proj_audit_group)
        userList = [u for u in audit_group.user_set.values('username', 'login_status')]

        if request.method == 'GET':
            return render(request, 'projs/deploy_apply.html', locals())


def ticket_list(request):

    if request.method == "GET":
        deploy_tickets = Project_Deploy_Ticket.objects.order_by("-id")[0:200]
        return render(request, 'projs/ticket_list.html', locals())

    elif request.method == "POST":
        if request.POST.get('model') in ['auth']:
            try:
                Project_Deploy_Ticket.objects.filter(id=request.POST.get('id')).update(
                    ticket_status=request.POST.get('ticket_status'),
                    ticket_cancel=request.POST.get('ticket_cancel', None),
                    modify_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                )
                if request.POST.get('model') == 'auth':
                    #sendDeployNotice.delay(order_id=request.POST.get('id'), mask='【已授权】')
                    pass
                elif request.POST.get('model') == 'finish':
                    #sendDeployNotice.delay(order_id=request.POST.get('id'), mask='【已部署】')
                    pass
                elif request.POST.get('model') == 'disable':
                    #sendDeployNotice.delay(order_id=request.POST.get('id'), mask='【已取消】')
                    pass
            except Exception as e:
                return JsonResponse({'msg': "操作失败：" + str(e), "code": 500, 'data': []})
            return JsonResponse({'msg': "操作成功", "code": 200, 'data': []})

        elif request.POST.get('model') in ['disable']:
            try:
                if request.user.is_superuser:
                    Project_Deploy_Ticket.objects.filter(id=request.POST.get('id')).update(
                        ticket_status=request.POST.get('ticket_status'),
                        ticket_cancel=request.POST.get('ticket_cancel', None),
                        modify_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    )
                else:
                    dr=Project_Deploy_Record.objects.filter(d_ticket_id=request.POST.get('id'))
                    if dr.count() == 0:
                        Project_Deploy_Ticket.objects.filter(id=request.POST.get('id')).update(
                            ticket_status=request.POST.get('ticket_status'),
                            ticket_cancel=request.POST.get('ticket_cancel', None),
                            modify_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                        )
                    else:
                        return JsonResponse({'msg': "已有发布记录，请联系管理员处理！", "code": 500, 'data': []})

                    # sendDeployNotice.delay(order_id=request.POST.get('id'), mask='【已取消】')
            except Exception as e:
                return JsonResponse({'msg': "操作失败：" + str(e), "code": 500, 'data': []})
            return JsonResponse({'msg': "操作成功", "code": 200, 'data': []})

        elif request.POST.get('model') in ['finish', 'rollback_finish']:
            try:
                count = 0
                rollback = 0
                config = Project_Deploy_Ticket.objects.get(id=request.POST.get('id'))
                if config.ticket_status == 0:
                    for pid in config.ticket_platform.all():
                        for ser in Assets.objects.filter(asset_projenv=config.ticket_config.proj_env.id).filter(
                                asset_platform=pid).filter(asset_projapp__id=config.ticket_config.proj_app.id):
                            dt = Project_Deploy_Record.objects.filter(deploy_ip=ser.asset_management_ip,
                                                                      d_ticket_id=request.POST.get('id'))

                            if request.POST.get('model') == 'finish':
                                if dt.count() == 0:
                                    if ser.asset_status == 0:
                                        count += 1
                                elif dt[0].deploy_status != 9 or dt[0].rollback_status == 1:
                                        count += 1
                            else:
                                if dt.count() != 0:
                                    count += 1
                                    if dt[0].rollback_status == 0:
                                        rollback += 1
                    if request.POST.get('model') == 'rollback_finish' and count == 0:
                        return JsonResponse({'msg': "检测到没有部署记录，请勿点回滚完成！", "code": 500, 'data': []})

                    elif  request.POST.get('model') == 'finish' and count == 0 or  request.POST.get('model') == 'rollback_finish' and rollback == 0:
                        try:
                            Project_Deploy_Ticket.objects.filter(id=request.POST.get('id')).update(
                                ticket_status=request.POST.get('ticket_status'),
                                ticket_cancel=request.POST.get('ticket_cancel', None),
                                modify_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                            )
                            return JsonResponse({'msg': "操作成功", "code": 200, 'data': []})
                        except Exception as e:
                            return JsonResponse({'msg': "操作失败：" + str(e), "code": 500, 'data': []})
                    else:
                        if request.POST.get('model') == 'finish':
                            return JsonResponse({'msg': "检测到有未部署或有回滚记录的主机", "code": 500, 'data': []})
                        else:
                            return JsonResponse({'msg': "检测到有未回滚的主机", "code": 500, 'data': []})
                else:
                    return JsonResponse({'msg': "不能重复修改工单状态", "code": 500, 'data': []})
            except Exception as e:
                return JsonResponse({'msg': "操作失败：" + str(e), "code": 500, 'data': []})


def deploy_ticket(request, pk):
    deploy_ticket = Project_Deploy_Ticket.objects.get(id=pk)
    if request.method == "GET":
        return render(request, 'projs/deploy_ticket.html', locals())

    elif request.method == "POST":
        if request.POST.get('query') in ['service', 'project', 'group', 'dserver']:
            pid = request.POST.get('pid')  # platformID
            serverList = []
            if request.POST.get('query') == 'dserver':
                for ser in Assets.objects.filter(asset_projenv=deploy_ticket.ticket_config.proj_env.id).filter(
                        asset_platform=pid).filter(asset_projapp__id=deploy_ticket.ticket_config.proj_app.id):
                    serverList.append({"id": ser.id, "ip": ser.asset_management_ip, "hs": ser.asset_hostname,
                                       "as": ser.asset_status})
            return JsonResponse({'msg': "主机查询成功", "code": 200, 'data': serverList})
        else:
            JsonResponse({'msg': "不支持的操作", "code": 500, 'data': []})
    else:
        return JsonResponse({'msg': "操作失败", "code": 500, 'data': "不支持的操作"})


@admin_auth
def deploy_log(request):
    start_time = request.GET.get('startTime')
    end_time = request.GET.get('endTime')

    if start_time and end_time:
        new_end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d') + datetime.timedelta(1)
        end_time = new_end_time.strftime('%Y-%m-%d')
        try:
            records = []
            search_records = Project_Deploy_Record.objects.select_related('d_ticket_id').select_related('assets').filter(
                create_date__gt=start_time, create_date__lt=end_time)
            for search_record in search_records:
                record = {
                    'id': search_record.id,
                    'ticket_no': search_record.d_ticket_id.ticket_no,
                    'ticket_env': search_record.d_ticket_id.ticket_config.proj_env.projenv_name,
                    'ticket_pltf': search_record.assets.asset_platform.platform_name,
                    'ticket_proj': search_record.d_ticket_id.ticket_config.proj_name.projname_name,
                    'ticket_app': search_record.d_ticket_id.ticket_config.proj_app.projapp_name,
                    'cid': search_record.d_ticket_id.ticket_commit[:7] + "-" + search_record.d_ticket_id.ticket_config.proj_branch_tag,
                    'host': search_record.deploy_ip,
                    'deploy': search_record.deploy_status,
                    'rollback': search_record.rollback_status,
                    'update_time': search_record.create_date,
                    'status': search_record.d_ticket_id.ticket_status
                }
                records.append(record)
            return JsonResponse({'code': 200, 'records': records})
        except Exception as e:
            return JsonResponse({'code': 500, 'error': '查询失败：{}'.format(e)})
    else:
        logs = Project_Deploy_Record.objects.select_related('d_ticket_id').select_related('assets').all()
        return render(request, 'projs/deploy_log.html', locals())


def check_log(request, pk):
    config = ProjectConfig.objects.prefetch_related('deploy_server').get(id=pk)
    server = config.deploy_server.first()
    host = server.assets.asset_management_ip
    port = server.port
    username = server.username
    password = server.password
    return render(request, 'projs/check_log.html',
                  {'host': host, 'port': port, 'username': username, 'password': password})
