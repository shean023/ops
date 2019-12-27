# _*_ coding: utf-8 _*_
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from ticket.models import *

@permission_required('projs.add_project', raise_exception=True)
def ticket_manage(request):
    return render(request, 'ticket/ticket_manage.html', locals())


@permission_required('projs.add_project', raise_exception=True)
def ticket_type(request):
    returnData = {'status': 0, 'message': '', 'data': []}  ## 请求返回结果数据
    if request.method == 'POST' and request.POST.get('oper') == "addCaseType":  ## 添加工单类型
        try:
            name = request.POST.get('name')
            createuser_id = request.user
            type_form = request.POST.get('type_form')
            status = request.POST.get('status')
            exec_model = request.POST.get('exec_model')
            audit_model = request.POST.get('audit_model')

        except Exception as e:
            returnData['status'] = 1
            returnData['message'] = '未能获取POST数据:' + str(e)
            return JsonResponse(returnData)
        else:
            try:
                ## 新增工单类型
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
                        order= exec_model.split(',').index(exec_user)
                    )
                ## 添加审核列表
                print(audit_model)
                for audit_user in audit_model.split(','):
                    TicketAuditModel.objects.create(
                        tt_id=tt,
                        user_id= int(audit_user),
                        order=audit_model.split(',').index(audit_user)
                    )

            except Exception as e:
                returnData['status'] = 1
                returnData['message'] = '插入数据失败:' + str(e)
                return JsonResponse(returnData)
            return JsonResponse(returnData)
        # casetype_name = str(request.form['casetype_name'])
        # casetype_executor = int(request.form['casetype_executor'])
        # casetype_checkleader = str(request.form['casetype_checkleader']).split(',')
        # casetype_status = int(request.form['casetype_status'])
        #
        # try:
        #     ## 新增工单类型
        #     addCaseType = casetype()
        #     addCaseType.name = casetype_name
        #     addCaseType.createuser_id = loginData['user']['id']
        #     addCaseType.status = casetype_status
        #     db.session.add(addCaseType)
        #
        #     ## 添加执行人
        #     addCaseExecModel = caseexecmodel()
        #     addCaseExecModel.case_type = addCaseType
        #     addCaseExecModel.user_id = casetype_executor
        #     addCaseExecModel.order = 0
        #     db.session.add(addCaseExecModel)
        #
        #     ## 添加审核列表
        #     for checkleader in casetype_checkleader:
        #         addCaseAuditModel = caseauditmodel()
        #         addCaseAuditModel.case_type = addCaseType
        #         addCaseAuditModel.user_id = int(checkleader)
        #         addCaseAuditModel.order = casetype_checkleader.index(checkleader)
        #         db.session.add(addCaseAuditModel)
        #     #
        #     db.session.commit()
        # except Exception as e:
        #     returnData['status'] = 1
        #     returnData['message'] = '新增失败:'+str(e)
        #     #db.session().rollback()

        # return Response(json.dumps(returnData), mimetype="application/json")
