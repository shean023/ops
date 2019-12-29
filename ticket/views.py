# _*_ coding: utf-8 _*_
from datetime import date

from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from kombu.utils import json

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
                user_record = UserProfile.objects.get(id = int(execModel.user_id))
                executor_name = user_record.cnname if user_record.cnname else user_record.username

            if executor_str == "":
                executor_str = "<span> " + str(executor_name) + " </span>"
            else:
                executor_str = executor_str + "<span class='glyphicon glyphicon-arrow-right'></span><span> " + str(executor_name) + " </span>"
        tmpData['exec_model'] = executor_str

        checkleader_str = ""
        for auditModel in tt.audit_model.all().order_by('order'):
            if str(auditModel.user_id) == "-1":
                checkleader_name = "默认上级"
            else:
                user_record = UserProfile.objects.get(id = int(auditModel.user_id))
                checkleader_name = user_record.cnname if user_record.cnname else user_record.username

            if checkleader_str == "":
                checkleader_str = "<span> " + str(checkleader_name) + " </span>"
            else:
                checkleader_str = checkleader_str + "<span class='glyphicon glyphicon-arrow-right'></span><span> " + str(checkleader_name) + " </span>"
        tmpData['audit_model'] = checkleader_str
    return render(request, 'ticket/ticket_manage.html',locals())


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
                    a=b=0
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
                            order= a,
                        )
                        a+=1
                    ## 添加审核列表
                    for audit_user in audit_model.split(','):
                        TicketAuditModel.objects.create(
                            tt_id=tt,
                            user_id= int(audit_user),
                            #order=audit_model.split(',').index(audit_user)
                            order= b,
                        )
                        b+=1
                    return JsonResponse({'code': 200, 'msg': '新增工单类型插入数据成功'})
                except Exception as e:
                    return JsonResponse({'code': 500, 'msg': '新增工单类型插入数据异常： {}'.format(e)})


        elif request.POST.get('oper') == "getCaseType":  ## 获取单条工单类型记录(为编辑工单准备数据)

            tt_id = int(request.POST.get('tt_id'))

            getData = TictetType.objects.get(id=tt_id)
            rData = {}
            rData['id'] = getData.id
            rData['name'] = getData.name
            rData['status'] = getData.status
            try:
                rData['executor'] = []
                for execModel in getData.exec_model.all().order_by('order'):
                    if execModel.user_id == "-1":
                        rData['executor'].append("-1_默认上级")
                    else:
                        executor = UserProfile.objects.get(id=execModel.user_id)
                        rData['executor'].append(str(executor.id) + "_" + str(executor.cnname if executor.cnname else executor.username) + "(" + str(executor.username) + ")")

                rData['checkleader'] = []
                for auditModel in getData.audit_model.all().order_by('order'):
                    if str(auditModel.user_id) == "-1":
                        rData['checkleader'].append("-1_默认上级")
                    else:
                        checkleader = UserProfile.objects.get(id=auditModel.user_id)
                        rData['checkleader'].append(str(checkleader.id) + "_" + str(checkleader.cnname if checkleader.cnname else checkleader.username) + "(" + str(checkleader.username) + ")")

                rData['users'] = []
                allUser = UserProfile.objects.filter().all()
                for record in allUser:
                    rData['users'].append({'id': record.id, 'name': record.username, 'cnname': record.cnname if record.cnname else record.username})
            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '获取工单类型异常： {}'.format(e)})
            else:
                return JsonResponse({'code': 200, 'msg': '获取工单类型成功', 'data': rData})

        elif request.POST.get('oper') == "editCaseType":  ##编辑工单类型
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
                    ##删除工单类型外键数据
                    tt = TictetType.objects.filter(id=id)
                    tt[0].exec_model.all().delete()
                    tt[0].audit_model.all().delete()
                except Exception as e:
                    return JsonResponse({'code': 500, 'msg': '编辑工单类型删除历史数据异常： {}'.format(e)})
                else:
                    try:
                        a = b = 0
                        tt.update(name=name, status=status)
                        ## 添加执行人
                        for exec_user in exec_model.split(','):
                            TicketExecModel.objects.create(
                                tt_id=tt[0],
                                user_id=int(exec_user),
                                order=a,
                            )
                            a += 1
                        ## 添加审核列表
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
        ## 添加工单
        if request.POST.get('oper') == "addCase":
            tt_id = int(request.POST.get('casetype'))
            title = str(request.POST.get('casetitle'))
            content = str(request.POST.get('caserequire'))
            result = str(request.POST.get('caseresult'))
            createuser_id = request.user
            get_tt = TictetType.objects.get(id=tt_id)

            status = 2  ## 判断是保存还是提交
            if str(request.POST.get('type')) == 'save': status = 1

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
                        t_id = ticket,
                        user_id = UserProfile.objects.get(id=audituser_id),
                        order = auditUser.order,
                        status = 0
                    )
                # ## 添加执行人
                for execUser in get_tt.exec_model.all():
                    TicketExec.objects.create(
                        t_id = ticket,
                        user_id = UserProfile.objects.get(id=execUser.user_id),
                        order = execUser.order,
                        status = 0,
                    )
                # # ## 添加操作步骤
                TicketOperation.objects.create(
                    t_id = ticket,
                    user_id=UserProfile.objects.get(id=request.user.id),
                    status = 1,
                    content = ""
                )
                return JsonResponse({'code': 200, 'msg': '创建工单成功'})
            except Exception as e:
                return JsonResponse({'code': 500, 'msg': '创建工单异常： {}'.format(e)})
            # ## 添加工单
            # addCase = case()
            # addCase.title = caseTitle
            # addCase.casetype_id = caseTypeID
            # addCase.createuser_id = loginData['user']['id']
            # addCase.content = caseRequire
            # addCase.result = caseResult
            # addCase.status = caseStatus
            # db.session.add(addCase)
            #
            # ## 添加审核人
            # for auditUser in getCaseType.audit_model:
            #     if auditUser.user_id == -1:
            #         leaderUser = user.query.filter(user.department_id == loginData['user']['department_id']).filter(
            #             user.leader == 0).first()
            #         audituser_id = leaderUser.id
            #     else:
            #         audituser_id = auditUser.user_id
            #
            #     addCaseAudit = caseaudit()
            #     addCaseAudit.case_rs = addCase
            #     addCaseAudit.user_id = audituser_id
            #     addCaseAudit.order = auditUser.order
            #     addCaseAudit.status = 0
            #     db.session.add(addCaseAudit)
            #
            # ## 添加执行人
            # for execUser in getCaseType.exec_model:
            #     addCaseExec = caseexec()
            #     addCaseExec.case_rs = addCase
            #     addCaseExec.user_id = execUser.user_id  ##后续需要修改
            #     addCaseExec.order = execUser.order
            #     addCaseExec.status = 0
            #     db.session.add(addCaseExec)
            #
            # ## 添加操作步骤
            # addCaseOperation = caseoperation()
            # addCaseOperation.case_rs = addCase
            # addCaseOperation.user_id = loginData['user']['id']
            # addCaseOperation.status = 1
            # addCaseOperation.content = ""
            # db.session.add(addCaseOperation)
            #
            # db.session.commit()
            #
            # return redirect("/case/mycreate/")

@permission_required('projs.add_project', raise_exception=True)
def ticket_execute(request):
    pass

@permission_required('projs.add_project', raise_exception=True)
def ticket_check(request):
    pass

@permission_required('projs.add_project', raise_exception=True)
def ticket_mycreate(request):
    pass

@permission_required('projs.add_project', raise_exception=True)
def ticket_history(request):
    pass