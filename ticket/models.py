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
























