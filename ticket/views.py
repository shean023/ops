# _*_ coding: utf-8 _*_
from datetime import date

from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from kombu.utils import json
from django.db.models import Q
from ticket.models import *
from users.models import UserProfile


@permission_required('projs.add_project', raise_exception=True)
def ticket_edit(request, pk):
    if request.method == 'DELETE' and pk:
        try:
            TictetType.objects.filter(id=pk).delete()
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '删除工单类型失败: {}'.format(e)})
        else:
            return JsonResponse({'code': 200, 'msg': ''})


@permission_required('projs.add_project', raise_exception=True)
def ticket_manage(request):
    users = UserProfile.objects.all
    tts = TictetType.objects.all().order_by('-id')
    ttDatas = []
    for tt in tts:
        tmpData = {'id': tt.id,
                   'name': tt.name,
                   'exec_model': "",
                   'audit_model': "",
                   'status': tt.status,
                   'ctime': tt.ctime,
                   }
        ttDatas.append(tmpData)

        executor_str = ""
        for execModel in tt.exec_model.all().order_by('order'):
            if str(execModel.user_id) == "-1":
                executor_name = "默认上级"
            else:
                user_record = UserProfile.objects.get(id=int(execModel.user_id))
                executor_name = user_record.cnname if user_record.cnname else user_record.username

            if executor_str == "":
                executor_str = "<span> " + str(executor_name) + " </span>"
            else:
                executor_str = executor_str + "<span class='glyphicon glyphicon-arrow-right'></span><span> " + str(
                    executor_name) + " </span>"
        tmpData['exec_model'] = executor_str

        checkleader_str = ""
        for auditModel in tt.audit_model.all().order_by('order'):
            if str(auditModel.user_id) == "-1":
                checkleader_name = "默认上级"
            else:
                user_record = UserProfile.objects.get(id=int(auditModel.user_id))
                checkleader_name = user_record.cnname if user_record.cnname else user_record.username

            if checkleader_str == "":
                checkleader_str = "<span> " + str(checkleader_name) + " </span>"
            else:
                checkleader_str = checkleader_str + "<span class='glyphicon glyphicon-arrow-right'></span><span> " + str(
                    checkleader_name) + " </span>"
        tmpData['audit_model'] = checkleader_str
    return render(request, 'ticket/ticket_manage.html', locals())


@permission_required('projs.add_project', raise_exception=True)
def ticket_type(request):
    if request.method == 'POST':
        if request.POST.get('oper') == "addCaseType":  ## 添加工单类型
            try:
                name = request.POST.get('name')
                createuser_id = request.user
                type_form = request.POST.get('type_form')
                status = request.POST.get('status')
                exec_model = request.POST.get('exec_model')
                audit_model = request.POST.get('audit_model')

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '新增工单类型POST获取数据异常： {}'.format(e)})
            else:
                try:
                    ## 新增工单类型
                    a = b = 0
                    tt = TictetType.objects.create(
                        name=name,
                        createuser_id=createuser_id,
                        type_form=type_form,
                        status=status
                    )
                    ## 添加执行人
                    for exec_user in exec_model.split(','):
                        TicketExecModel.objects.create(
                            tt_id=tt,
                            user_id=int(exec_user),
                            order=a,
                        )
                        a += 1
                    ## 添加审核列表
                    for audit_user in audit_model.split(','):
                        TicketAuditModel.objects.create(
                            tt_id=tt,
                            user_id=int(audit_user),
                            # order=audit_model.split(',').index(audit_user)
                            order=b,
                        )
                        b += 1
                    return JsonResponse({'code': 200, 'msg': '新增工单类型插入数据成功'})
                except Exception as e:
                    try:
                        TictetType.objects.get(id=tt).delete()
                    except Exception as e:
                        pass
                    return JsonResponse({'code': 500, 'msg': '新增工单类型插入数据异常： {}'.format(e)})

        # 获取单条工单类型记录(为编辑工单准备数据)
        elif request.POST.get('oper') == "getCaseType":

            tt_id = int(request.POST.get('tt_id'))

            getData = TictetType.objects.get(id=tt_id)
            rData = {'id': getData.id, 'name': getData.name, 'status': getData.status}
            try:
                rData['executor'] = []
                for execModel in getData.exec_model.all().order_by('order'):
                    if str(execModel.user_id) == "-1":

                        rData['executor'].append("-1_默认上级")

                    else:
                        executor = UserProfile.objects.get(id=execModel.user_id)
                        rData['executor'].append(str(executor.id) + "_" + str(
                            executor.cnname if executor.cnname else executor.username) + "(" + str(
                            executor.username) + ")")

                rData['checkleader'] = []
                for auditModel in getData.audit_model.all().order_by('order'):
                    if str(auditModel.user_id) == "-1":
                        rData['checkleader'].append("-1_默认上级")
                    else:
                        checkleader = UserProfile.objects.get(id=auditModel.user_id)
                        rData['checkleader'].append(str(checkleader.id) + "_" + str(
                            checkleader.cnname if checkleader.cnname else checkleader.username) + "(" + str(
                            checkleader.username) + ")")

                rData['users'] = []
                allUser = UserProfile.objects.filter().all()
                for record in allUser:
                    rData['users'].append({'id': record.id, 'name': record.username,
                                           'cnname': record.cnname if record.cnname else record.username})
            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '获取工单类型异常： {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '获取工单类型成功', 'data': rData})

        elif request.POST.get('oper') == "editCaseType":  # 编辑工单类型
            try:
                id = request.POST.get('casetype_id')
                name = request.POST.get('name')
                status = request.POST.get('status')
                exec_model = request.POST.get('exec_model')
                audit_model = request.POST.get('audit_model')
            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '编辑工单类型获取数据异常: {}'.format(e)})
            else:
                try:
                    # 删除工单类型外键数据
                    tt = TictetType.objects.filter(id=id)
                    tt[0].exec_model.all().delete()
                    tt[0].audit_model.all().delete()
                except Exception as e:
                    return JsonResponse({'code': 500, 'msg': '编辑工单类型删除历史数据异常： {}'.format(e)})
                else:
                    try:
                        a = b = 0
                        tt.update(name=name, status=status)
                        # 添加执行人
                        for exec_user in exec_model.split(','):
                            TicketExecModel.objects.create(
                                tt_id=tt[0],
                                user_id=int(exec_user),
                                order=a,
                            )
                            a += 1
                        # 添加审核列表
                        for audit_user in audit_model.split(','):
                            TicketAuditModel.objects.create(
                                tt_id=tt[0],
                                user_id=int(audit_user),
                                # order=audit_model.split(',').index(audit_user)
                                order=b,
                            )
                            b += 1
                        return JsonResponse({'code': 200, 'msg': '编辑工单类型更新数据成功'})
                    except Exception as e:
                        return JsonResponse({'code': 500, 'msg': '编辑工单类型更新数据异常： {}'.format(e)})


@permission_required('projs.add_project', raise_exception=True)
def ticket_create(request):
    if request.method == 'GET':
        tts = TictetType.objects.all()
        return render(request, 'ticket/ticket_create.html', locals())

    elif request.method == 'POST':
        # 添加工单
        if request.POST.get('oper') == "addCase":
            tt_id = int(request.POST.get('casetype'))
            title = str(request.POST.get('casetitle'))
            content = str(request.POST.get('caserequire'))
            result = str(request.POST.get('caseresult'))
            createuser_id = request.user
            get_tt = TictetType.objects.get(id=tt_id)

            status = 2  # 判断是保存还是提交
            if str(request.POST.get('type')) == 'save':
                status = 1

            try:
                ticket = Ticket.objects.create(
                    title=title,
                    tt_id=get_tt,
                    createuser_id=createuser_id,
                    content=content,
                    result=result,
                    status=status
                )
                # ## 添加审核人
                for auditUser in get_tt.audit_model.all():
                    if auditUser.user_id == -1:
                        leaderUser = UserProfile.objects.filter(department_id=request.user.department_id, leader=0)
                        if leaderUser.count():
                            audituser_id = leaderUser[0].id
                        else:
                            Ticket.objects.get(id=ticket.id).delete()
                            return JsonResponse({'code': 500, 'msg': '没有部门负责人，请联系管理员！'})
                    else:
                        audituser_id = auditUser.user_id

                    TicketAudit.objects.create(
                        t_id=ticket,
                        user_id=UserProfile.objects.get(id=audituser_id),
                        order=auditUser.order,
                        status=0
                    )
                # 添加执行人
                for execUser in get_tt.exec_model.all():
                    if execUser.user_id == -1:
                        leaderUser = UserProfile.objects.filter(department_id=request.user.department_id, leader=0)
                        if leaderUser.count():
                            execUser_id = leaderUser[0].id
                        else:
                            Ticket.objects.get(id=ticket.id).delete()
                            return JsonResponse({'code': 500, 'msg': '没有部门负责人，请联系管理员！'})
                    else:
                        execUser_id = execUser.user_id

                    TicketExec.objects.create(
                        t_id=ticket,
                        user_id=UserProfile.objects.get(id=execUser_id),
                        order=execUser.order,
                        status=0,
                    )
                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=ticket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=1 if status == 2 else 0,
                    content=""
                )
                return JsonResponse({'code': 200, 'msg': '创建工单成功', 'ticketid': ticket.id})
            except Exception as e:
                try:
                    Ticket.objects.get(id=ticket).delete()
                except Exception as e:
                    pass
                return JsonResponse({'code': 500, 'msg': '创建工单异常： {}'.format(e)})


@permission_required('projs.add_project', raise_exception=True)
def ticket_execute(request):
    if request.method == 'GET':
        # 执行工单详情
        if request.GET.get('type') == 'detail':
            detailData = {}
            getTicket = Ticket.objects.get(id=request.GET.get('mtid'))
            detailData.update({'ticket_id': getTicket.id,
                               'ticket_title': getTicket.title,
                               'ticket_createuser': getTicket.createuser_id.username,
                               'ticket_result': getTicket.result,
                               'ticket_content': getTicket.content,
                               'ticket_status': getTicket.status,
                               'ticket_status_label': getTicket.get_status_display(),
                               'ticket_ctime': getTicket.ctime,
                               'ticket_type': getTicket.tt_id.name,
                               })

            detailData.update({'audit_user': []})
            for auditUser in getTicket.ticketaudit_set.all():
                detailData['audit_user'].append({'name': auditUser.user_id.username, 'status': auditUser.status})

            detailData.update({'exec_user': []})
            for execUser in getTicket.ticketexec_set.all():
                detailData['exec_user'].append({'name': execUser.user_id.username, 'status': execUser.status})

            detailData.update({'operation_user': []})
            for operationUser in getTicket.ticketoperation_set.all():
                detailData['operation_user'].append({
                    'name': operationUser.user_id.username,
                    'operation_type': operationUser.get_status_display(),
                    'content': operationUser.content,
                    'ctime': operationUser.ctime,
                    'login_status': operationUser.user_id.login_status,
                    'user_image': operationUser.user_id.image
                })
            return render(request, 'ticket/ticket_myexecute_detail.html', locals())

        # 执行工单列表
        else:
            ttDatas = []
            allData = Ticket.objects.filter(Q(status__in=([3, 4, 5, 6, 8, 9])))
            for record in allData:
                if not record.ticketexec_set.all()[record.execNum].user_id.id == request.user.id:
                    continue

                userName = record.ticketexec_set.all()[record.execNum].user_id.username

                tmpData = {'id': record.id,
                           'title': record.title,
                           'casetype': record.tt_id.name,
                           'user': userName,
                           'status_choice': record.get_status_display(),
                           'status': record.status,
                           'ctime': record.ctime,
                           }
                ttDatas.append(tmpData)

            return render(request, 'ticket/ticket_myexecute.html', locals())

    elif request.method == 'POST':
        # 执行OK
        if request.POST.get('type') == 'ExecOK':
            try:
                ticket_id = int(request.POST.get('ticketid'))
                getTicket = Ticket.objects.get(id=ticket_id)

                # execNum = getTicket.execNum
                # if execNum + 1 == len(getTicket.ticketexec_set.all()):
                #     getTicket.status = 4
                # else:
                #     getTicket.execNum = execNum + 1
                #     getTicket.status = 4

                getTicket.status = 4
                getTicket.save()

                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=getTicket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=5,
                    content=' exec in process'
                )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})

        # 执行no
        elif request.POST.get('type') == 'ExecNO':
            try:
                ticket_id = int(request.POST.get('ticketid'))
                getTicket = Ticket.objects.get(id=ticket_id)
                getTicket.status = 8
                getTicket.auditNum = 0
                getTicket.execNum = 0
                getTicket.save()

                # 修改审核人状态
                TicketAudit.objects.filter(t_id=getTicket.id).update(status=0)
                TicketExec.objects.filter(t_id=getTicket.id).update(status=0)

                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=getTicket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=6,
                    content='exec no'
                )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})

        # 执行转发
        elif request.POST.get('type') == 'ExecForwarding':
            try:
                ticket_id = int(request.POST.get('ticketid'))
                user_id = int(request.POST.get('executor_id'))

                getTicket = Ticket.objects.get(id=ticket_id)
                getUser = UserProfile.objects.get(id=user_id)

                getTicketExec = TicketExec.objects.get(t_id=getTicket.id, order=getTicket.execNum)
                getTicketExec.user_id = getUser
                getTicketExec.save()

                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=getTicket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=9,
                    content=str(request.user.username + "  Forwarding To  " + str(getUser.username))
                )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})

        elif request.POST.get('type') == 'execComplete' or request.POST.get('type') == 'execSave':
            try:
                ticket_id = int(request.POST.get('ticketid'))
                ticket_result = str(request.POST.get('ticketresult'))

                getTicket = Ticket.objects.get(id=ticket_id)

                # 判断是保存还是执行完成
                status = 5
                if request.POST.get('type') == 'execComplete':
                    execNum = getTicket.execNum
                    if execNum + 1 == len(getTicket.ticketexec_set.all()):
                        status = 6
                    else:
                        getTicket.execNum = execNum + 1
                        status = 3

                    getTicketExec = TicketExec.objects.get(t_id=getTicket, order=execNum)
                    getTicketExec.status = 1
                    getTicketExec.save()

                if getTicket.status != 9 or status == 6:
                    getTicket.status = status

                getTicket.result = ticket_result
                getTicket.save()

                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=getTicket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=status + 2 if status == 5 or status == 6 else status + 5,
                    content=""
                )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})


@permission_required('projs.add_project', raise_exception=True)
def ticket_check(request):
    if request.method == 'GET':

        # 我的创建工单－工单详情
        if request.GET.get('type') == 'detail':
            detailData = {}
            getTicket = Ticket.objects.get(id=request.GET.get('mtid'))
            detailData.update({'ticket_id': getTicket.id,
                               'ticket_title': getTicket.title,
                               'ticket_createuser': getTicket.createuser_id.username,
                               'ticket_result': getTicket.result,
                               'ticket_content': getTicket.content,
                               'ticket_status': getTicket.status,
                               'ticket_status_label': getTicket.get_status_display(),
                               'ticket_ctime': getTicket.ctime,
                               'ticket_type': getTicket.tt_id.name,
                               })

            detailData.update({'audit_user': []})
            for auditUser in getTicket.ticketaudit_set.all():
                detailData['audit_user'].append({'name': auditUser.user_id.username, 'status': auditUser.status})

            detailData.update({'exec_user': []})
            for execUser in getTicket.ticketexec_set.all():
                detailData['exec_user'].append({'name': execUser.user_id.username, 'status': execUser.status})

            detailData.update({'operation_user': []})
            for operationUser in getTicket.ticketoperation_set.all():
                detailData['operation_user'].append({
                    'name': operationUser.user_id.username,
                    'operation_type': operationUser.get_status_display(),
                    'content': operationUser.content,
                    'ctime': operationUser.ctime,
                    'login_status': operationUser.user_id.login_status,
                    'user_image': operationUser.user_id.image
                })
            return render(request, 'ticket/ticket_mycheck_detail.html', locals())

        else:  # 我的审核工单列表
            ttDatas = []
            allData = Ticket.objects.filter(Q(status__in=([2, 7])))
            for record in allData:
                if not record.ticketaudit_set.all()[record.auditNum].user_id.id == request.user.id:
                    continue
                if record.status == 2:
                    userName = TicketAudit.objects.filter(t_id=record.id).filter(
                        order=record.auditNum).first().user_id.username
                elif record.status in [3, 4, 5, 9]:
                    userName = TicketExec.objects.filter(t_id=record.id).filter(
                        order=record.execNum).first().user_id.username
                else:
                    userName = record.createuser_id.username

                tmpData = {'id': record.id,
                           'title': record.title,
                           'casetype': record.tt_id.name,
                           'user': userName,
                           'status_choice': record.get_status_display(),
                           'status': record.status,
                           'ctime': record.ctime,
                           }
                ttDatas.append(tmpData)

            return render(request, 'ticket/ticket_mycheck.html', locals())

    elif request.method == 'POST':
        # 审核ok
        if request.POST.get('type') == 'Checkok':
            try:
                ticket_id = int(request.POST.get('ticketid'))
                getTicket = Ticket.objects.get(id=ticket_id)

                auditNum = getTicket.auditNum
                if auditNum + 1 == len(getTicket.ticketaudit_set.all()):
                    getTicket.status = 3
                else:
                    getTicket.auditNum = auditNum + 1
                    getTicket.status = 2
                getTicket.save()

                getTicketAudit = TicketAudit.objects.get(t_id=getTicket.id, order=auditNum)
                getTicketAudit.status = 1
                getTicketAudit.save()

                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=getTicket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=2,
                    content='check ok'
                )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})

        # 审核no
        elif request.POST.get('type') == 'Checkno':
            try:
                ticket_id = int(request.POST.get('ticketid'))
                getTicket = Ticket.objects.get(id=ticket_id)
                getTicket.status = 7
                getTicket.auditNum = 0
                getTicket.execNum = 0
                getTicket.save()

                # 修改审核人状态
                TicketAudit.objects.filter(t_id=getTicket.id).update(status=0)

                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=getTicket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=3,
                    content='check no'
                )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})

        elif request.POST.get('type') == 'TicketForwarding':
            try:
                ticket_id = int(request.POST.get('ticketid'))
                forwarding_user_id = int(request.POST.get('checkleader_id'))

                getTicket = Ticket.objects.get(id=ticket_id)
                getUser = UserProfile.objects.get(id=forwarding_user_id)
                getTicketAudit = TicketAudit.objects.get(t_id=getTicket.id, order=getTicket.auditNum)
                getTicketAudit.user_id = getUser
                getTicketAudit.save()

                # 添加操作步骤
                TicketOperation.objects.create(
                    t_id=getTicket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=4,
                    content=str(request.user.username + "  Forwarding To  " + str(getUser.username))
                )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})


@permission_required('projs.add_project', raise_exception=True)
def ticket_mycreate(request):
    # 我的创建工单列表

    if request.method == 'GET':
        # 我的创建工单－工单详情
        if request.GET.get('type') == 'detail':
            detailData = {}
            getTicket = Ticket.objects.get(id=request.GET.get('mtid'))
            detailData.update({'ticket_id': getTicket.id,
                               'ticket_title': getTicket.title,
                               'ticket_createuser': getTicket.createuser_id.username,
                               'ticket_result': getTicket.result,
                               'ticket_content': getTicket.content,
                               'ticket_status': getTicket.status,
                               'ticket_status_label': getTicket.get_status_display(),
                               'ticket_ctime': getTicket.ctime,
                               'ticket_type': getTicket.tt_id.name,
                               })

            detailData.update({'audit_user': []})
            for auditUser in getTicket.ticketaudit_set.all():
                detailData['audit_user'].append({'name': auditUser.user_id.username, 'status': auditUser.status})

            detailData.update({'exec_user': []})
            for execUser in getTicket.ticketexec_set.all():
                detailData['exec_user'].append({'name': execUser.user_id.username, 'status': execUser.status})

            detailData.update({'operation_user': []})
            for operationUser in getTicket.ticketoperation_set.all():
                detailData['operation_user'].append({
                    'name': operationUser.user_id.username,
                    'operation_type': operationUser.get_status_display(),
                    'content': operationUser.content,
                    'ctime': operationUser.ctime,
                    'login_status': operationUser.user_id.login_status,
                    'user_image': operationUser.user_id.image
                })
            return render(request, 'ticket/ticket_mycreate_detail.html', locals())

        else:  # 我的创建工单列表
            ttDatas = []
            allData = Ticket.objects.filter(
                Q(createuser_id=request.user.id) & Q(status__in=([1, 2, 3, 4, 5, 6, 7, 8, 9])))
            for record in allData:
                if record.status == 2:
                    userName = TicketAudit.objects.filter(t_id=record.id).filter(
                        order=record.auditNum).first().user_id.username
                elif record.status in [3, 4, 5, 9]:
                    userName = TicketExec.objects.filter(t_id=record.id).filter(
                        order=record.execNum).first().user_id.username
                else:
                    userName = record.createuser_id.username

                tmpData = {'id': record.id,
                           'title': record.title,
                           'casetype': record.tt_id.name,
                           'user': userName,
                           'status_choice': record.get_status_display(),
                           'status': record.status,
                           'ctime': record.ctime,
                           }
                ttDatas.append(tmpData)

            return render(request, 'ticket/ticket_mycreate.html', locals())

    elif request.method == 'POST':
        if request.POST.get('type') == 'sendMessage':
            # 添加操作记录
            try:
                ticketid = int(request.POST.get('ticketid'))
                message = str(request.POST.get('message'))
                TicketOperation.objects.create(
                    t_id=Ticket.objects.get(id=ticketid),
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=15,
                    content=message
                )
            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': ''})

        # 提交或保存工单
        elif request.POST.get('type') == 'editTicket':
            try:
                # 编辑工单
                ticketid = int(request.POST.get('ticketid'))
                ticketrequire = str(request.POST.get('ticketrequire')).strip()

                getTicket = Ticket.objects.filter(id=ticketid, createuser_id=request.user.id)

                # 判断是保存还是提交
                ticketstatus = 2
                operationstatus = 1
                if request.POST.get('action') == 'save':   # 保存工单
                    ticketstatus = 1
                if request.POST.get('action') == 'reset':  # 执行重做
                    ticketstatus = 9
                    operationstatus = 10
                    ticketexecNum = 0
                    TicketExec.objects.filter(t_id=ticketid).update(
                        status=0,
                    )
                    getTicket.update(execNum=ticketexecNum)

                if request.POST.get('action') == 'close':  # 关闭工单
                    ticketstatus = 10
                    operationstatus = 11
                    if getTicket[0].status == 7 or getTicket[0].status == 8:
                        ticketstatus = 11

                ##
                getTicket.update(
                    content=ticketrequire,
                    status=ticketstatus
                )

                ## 添加操作步骤
                TicketOperation.objects.create(
                    t_id=Ticket.objects.get(id=ticketid),
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status=0 if ticketstatus == 1 else operationstatus,
                    content=''
                )
            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})

        # 撤回或删除工单
        elif request.POST.get('type') == 'operTicket':

            try:

                ticketid = int(request.POST.get('ticketid'))
                getTicket = Ticket.objects.filter(id=ticketid)

                if request.POST.get('action') == 'deleteticket':
                    ## 删除工单
                    if getTicket[0].status in [1, 2, 3, 7, 11, 12]:
                        getTicket[0].delete()

                elif request.POST.get('action') == 'revoketicket':
                    # 撤回工单
                    getTicket.update(
                        status=1,
                        auditNum=0,
                        execNum=0
                    )

                    # 修改审核人状态
                    TicketAudit.objects.filter(t_id=ticketid).update(
                        status=0
                    )

                    # 修改执行人状态
                    TicketExec.objects.filter(t_id=ticketid).update(
                        status=0
                    )

                    # 添加操作步骤
                    TicketOperation.objects.create(
                        t_id=getTicket[0],
                        user_id=UserProfile.objects.get(id=request.user.id),
                        status=14,
                        content="revoke Ticket"
                    )

            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '添加操作记录失败: {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '操作成功！'})


@permission_required('projs.add_project', raise_exception=True)
def ticket_mydel(request, pk):
    if request.method == 'DELETE' and pk:
        try:
            if Ticket.objects.get(id=pk).status in [1, 2, 3, 7, 11, 12]:
                Ticket.objects.get(id=pk).delete()
            else:
                return JsonResponse({'code': 417, 'msg': '工单进入执行状态，不允许删除！请与管理员联系'})
        except Exception as e:
            return JsonResponse({'code': 500, 'msg': '删除工单类型失败: {}'.format(e)})
        else:
            return JsonResponse({'code': 200, 'msg': ''})


@permission_required('projs.add_project', raise_exception=True)
def ticket_history(request):
    if request.method == 'GET':
        if request.GET.get('type') == 'detail':
            detailData = {}
            getTicket = Ticket.objects.get(id=request.GET.get('mtid'))
            detailData.update({'ticket_id': getTicket.id,
                               'ticket_title': getTicket.title,
                               'ticket_createuser': getTicket.createuser_id.username,
                               'ticket_result': getTicket.result,
                               'ticket_content': getTicket.content,
                               'ticket_status': getTicket.status,
                               'ticket_status_label': getTicket.get_status_display(),
                               'ticket_ctime': getTicket.ctime,
                               'ticket_type': getTicket.tt_id.name,
                               })

            detailData.update({'audit_user': []})
            for auditUser in getTicket.ticketaudit_set.all():
                detailData['audit_user'].append({'name': auditUser.user_id.username, 'status': auditUser.status})

            detailData.update({'exec_user': []})
            for execUser in getTicket.ticketexec_set.all():
                detailData['exec_user'].append({'name': execUser.user_id.username, 'status': execUser.status})

            detailData.update({'operation_user': []})
            for operationUser in getTicket.ticketoperation_set.all():
                detailData['operation_user'].append({
                    'name': operationUser.user_id.username,
                    'operation_type': operationUser.get_status_display(),
                    'content': operationUser.content,
                    'ctime': operationUser.ctime,
                    'login_status': operationUser.user_id.login_status,
                    'user_image': operationUser.user_id.image
                })
            return render(request, 'ticket/ticket_myhistory_detail.html', locals())

        else:
            ttDatas = []
            allData = Ticket.objects.filter(Q(status__in=([10, 11, 12])))
            for record in allData:
                if not record.ticketaudit_set.all()[record.auditNum].user_id.id == request.user.id:
                    continue

                tmpData = {'id': record.id,
                           'title': record.title,
                           'casetype': record.tt_id.name,
                           'status_choice': record.get_status_display(),
                           'status': record.status,
                           'ctime': record.ctime,
                           }
                ttDatas.append(tmpData)

            return render(request, 'ticket/ticket_myhistory.html', locals())
