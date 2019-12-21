# -*- coding: utf-8 -*-
from django.db import models

#Create your models here.

class  Config_Confd(models.Model):
    asset_projenv = models.ForeignKey('assets.ProjectEnv', on_delete=models.PROTECT, verbose_name='环境')
    asset_proj = models.ForeignKey('assets.ProjectName', on_delete=models.PROTECT, verbose_name='项目')
    asset_projapp = models.ForeignKey('assets.ProjectApp', on_delete=models.PROTECT, verbose_name='应用')
    asset_platform = models.ForeignKey("assets.platformname", on_delete=models.PROTECT, related_name='confd_platform',blank=False, verbose_name='平台')
    confd_name = models.CharField(max_length=40, verbose_name='配置名称')
    confd_ns = models.CharField(max_length=40, verbose_name='命名空间')
    confd_memo = models.TextField(blank=True, verbose_name='项目描述', default='')

    class Meta:
        db_table = 'ops_config_confd'
        unique_together = ("asset_projenv", "asset_proj", "asset_projapp", "asset_platform", "confd_name", "confd_ns")
        permissions = (
            ("confd_projs", "读取confd_projs列表权限"),
        )
        verbose_name = '配置表'
        verbose_name_plural = '配置表'


class  Confd_Detail(models.Model):
    STATUS = (
        (0, '已发布|正常'),
        (1, '未发布|新'),
        (2, '无|改'),
        (3, '无|删'),
    )

    confd_name = models.ForeignKey('Config_Confd', on_delete=models.CASCADE, verbose_name='配置名称')
    confd_ns = models.CharField(max_length=40, verbose_name='命名空间')
    confd_key = models.CharField(max_length=40, verbose_name='键')
    confd_value  = models.CharField(max_length=40, verbose_name='值')
    confd_memo  = models.CharField(max_length=40, blank=True, verbose_name='备注')
    confd_deploy_status = models.IntegerField(choices=STATUS, default=1, verbose_name='发布状态')
    confd_status = models.IntegerField(choices=STATUS, default=1, verbose_name='key状态')
    confd_modified_user = models.CharField(max_length=40, verbose_name='最后修改用户')
    confd_modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_confd_detail'
        unique_together = ("confd_name","confd_ns", "confd_key")
        permissions = (
            ("confd_detail", "读取confd_detail列表权限"),
        )
        verbose_name = '配置明细'
        verbose_name_plural = '配置明细'


