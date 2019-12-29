from django.db import models


class TictetType(models.Model):
    """工单类型表"""
    STATUS = (
        (1, '启用'),
        (2, '禁用'),
        (3, '删除'),
    )

    name = models.CharField(max_length=64, verbose_name='工单类型名称')
    createuser_id = models.ForeignKey('users.UserProfile', related_name='tt_create', verbose_name='工单类型创建人',
                                      on_delete=models.PROTECT)
    confirm_duration = models.IntegerField(default='30', verbose_name='默认确认时长（分）')
    exec_duration = models.IntegerField(default='30', verbose_name='默认执行时长（分）')
    effective_date = models.IntegerField(default='5', verbose_name='默认有效期（天）')
    type_form = models.CharField(max_length=64, blank=True, null=True,verbose_name='工单类型表单')
    ctime = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='工单类型创建时间')
    mtime = models.DateTimeField(auto_now=True, blank=True, verbose_name='工单类型最后修改时间')
    status = models.IntegerField(choices=STATUS, default='1', verbose_name='工单状态')

    class Meta:
        db_table = 'ops_ticket_type'
        permissions = (
            ("ticket_type_read", "读取工单类型权限"),
            ("ticket_type_write", "写入工单类型权限"),
        )
        verbose_name = '工单类型表'
        verbose_name_plural = '工单类型表：创建工单执行流程和审核流程及工单响应时间'
        unique_together = ("name", "type_form")

class TicketExecModel(models.Model):
    """
    执行流程（多个执行）
    """
    tt_id = models.ForeignKey('TictetType', related_name='exec_model', verbose_name='工单类型表',
                                      on_delete=models.CASCADE)
    user_id = models.IntegerField(verbose_name='执行人（可以配置负数表示自动执行）')
    order = models.SmallIntegerField(verbose_name='执行顺序')

    class Meta:
        db_table = 'ops_ticket_execmodel'
        verbose_name = '执行流程表'
        verbose_name_plural = '执行流程'

class TicketAuditModel(models.Model):
    """
    审核流程（多个审核人）
    """
    tt_id = models.ForeignKey('TictetType', related_name='audit_model', verbose_name='工单类型表',
                              on_delete=models.CASCADE)
    user_id = models.IntegerField(verbose_name='执行人（可以配置负数表示自动执行）')
    order = models.SmallIntegerField(verbose_name='执行顺序')

    class Meta:
        db_table = 'ops_ticket_auditmodel'
        verbose_name = '执行流程表'
        verbose_name_plural = '执行流程'

class Ticket(models.Model):
    '''
    需求工单
    '''

    title = models.CharField(max_length=64, verbose_name='工单标题')
    tt_id = models.ForeignKey('TictetType', verbose_name='工单类型',on_delete=models.DO_NOTHING)
    createuser_id = models.ForeignKey('users.UserProfile', verbose_name='工单创建人',on_delete=models.DO_NOTHING)
    content = models.TextField(blank=True, null=True, verbose_name='工单需求 json 数据')
    result = models.TextField(blank=True, null=True, verbose_name='工单结果 json 数据')
    auditNum = models.SmallIntegerField(blank=False, null=False, default=0,verbose_name='第几个审核人, 为当前审核人（顺序)')
    execNum = models.SmallIntegerField(blank=False, null=False, default=0,verbose_name='第几个执行人，为当前执行人（顺序）')
    # 审核状态
    STATUS = ((1, '待提交'),
                  (2, '审核中'),
                  (3, '执行人确认中'),
                  (4, '执行人执行中'),
                  (5, '执行人延期执行中'),
                  (6, '执行完成,用户确认中'),
                  (7, '审核驳回,等待用户确认'),
                  (8, '执行驳回,等待用户确认'),
                  (9, '用户确认不通过,等待执行重做'),
                  (10, '完成关闭'),
                  (11, '驳回关闭'),
                  (12, '撤销关闭'),
                  )
    status = models.IntegerField(choices=STATUS, default='2', verbose_name='工单状态')
    ctime = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='工单创建时间')
    mtime = models.DateTimeField(auto_now=True, blank=True, verbose_name='工单最后修改时间')
    auditflow = models.SmallIntegerField(blank=False, null=False, default=0,verbose_name='执行流')
    execflow = models.SmallIntegerField(blank=False, null=False, default=0,verbose_name='审核流')
    operation = models.SmallIntegerField(blank=False, null=False, default=0,verbose_name='操作记录')

    class Meta:
        db_table = 'ops_ticket_ticket'
        verbose_name = '执行流程表'
        verbose_name_plural = '执行流程'


class TicketAudit(models.Model):
    '''
    工单审核流程（多个审核人）
    '''
    STATUS = (
        (0, '未审核'),
        (1, '已审核'),
    )

    t_id = models.ForeignKey('Ticket', verbose_name='工单id', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.UserProfile', on_delete=models.DO_NOTHING, verbose_name='审核人')
    order = models.SmallIntegerField(blank=False, null=False, verbose_name='审核顺序')
    status = models.IntegerField(choices=STATUS, default='0', verbose_name='执行状态')

    class Meta:
        db_table = 'ops_ticket_audit'
        verbose_name = '执行流程表'
        verbose_name_plural = '执行流程'


class TicketExec(models.Model):
    '''
    工单执行人流程（多个执行人）
    '''
    STATUS = (
        (0, '未审核'),
        (1, '已审核'),
    )

    t_id = models.ForeignKey('Ticket', verbose_name='工单id', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.UserProfile', on_delete=models.DO_NOTHING, verbose_name='审核人')
    order = models.SmallIntegerField(blank=False, null=False, verbose_name='审核顺序')
    status = models.IntegerField(choices=STATUS, default='0', verbose_name='执行状态')

    class Meta:
        db_table = 'ops_ticket_exec'
        verbose_name = '执行流程表'
        verbose_name_plural = '执行流程'


class TicketOperation(models.Model):
    '''
    工单操作表
    '''
    STATUS = (
        (1, '提交'),
        (2, '审核通过'),
        (3, '审核不通过'),
        (4, '审核转发'),
        (5, '确认执行'),
        (6, '执行确认不通过'),
        (7, '延期执行'),
        (8, '执行完成'),
        (9, '执行转发'),
        (10, '用户确认不通过'),
        (11, '关闭'),
        (12,' 重走流程'),
        (13, '重新编辑'),
        (14, '撤回工单'),
        (15, '回复'),
    )

    t_id = models.ForeignKey('Ticket', verbose_name='工单id', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.UserProfile', on_delete=models.DO_NOTHING, verbose_name='操作人')
    status = models.IntegerField(choices=STATUS, default='1', verbose_name='操作类型')
    content = models.TextField(blank=True, null=True, verbose_name='回复内容')
    ctime = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='创建时间')

    class Meta:
        db_table = 'ops_ticket_operation'
        verbose_name = '执行流程表'
        verbose_name_plural = '执行流程'






















