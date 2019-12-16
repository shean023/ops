from django.db import models
import uuid

class Project(models.Model):
    """项目表"""
    project_envs = (
        ('test', '测试环境'),
        ('fz', '仿真环境'),
        ('prod', '生产环境')
    )

    project_name = models.CharField(max_length=64, verbose_name='项目名称')
    project_env = models.CharField(max_length=4, choices=project_envs, verbose_name='项目环境', default='test')
    project_web = models.CharField(max_length=64, blank=True, verbose_name='项目网址', default='')
    project_admin = models.ForeignKey('users.UserProfile', related_name='proj_admin', verbose_name='项目负责人',
                                      on_delete=models.PROTECT)
    project_member = models.ManyToManyField('users.UserProfile', related_name='proj_member', blank=True,
                                            verbose_name='项目成员')
    project_org = models.TextField(blank=True, default='', verbose_name='项目架构JSON数据')
    project_memo = models.TextField(blank=True, verbose_name='项目描述', default='')

    class Meta:
        db_table = 'ops_project'
        permissions = (
            ("view_project", "读取项目列表权限"),
            ("deploy_project", "代码发布权限"),
        )
        verbose_name = '项目表'
        verbose_name_plural = '项目表'
        unique_together = ("project_env", "project_name")


class ProjectConfig(models.Model):
    project_models = (
        ('svn', 'svn'),
        ('git', 'git')
    )
    repo_models = (
        ('branch', 'branch'),
        ('tag', 'tag'),
        ('trunk', 'trunk'),
    )
    project_role = models.CharField(max_length=20, verbose_name='项目角色名称', null=False, blank=False)
    repo = models.CharField(choices=project_models, max_length=3, verbose_name='仓库类型')
    repo_user = models.CharField(max_length=10, verbose_name='仓库用户名', blank=True, default='')
    repo_password = models.CharField(max_length=16, verbose_name='仓库密码', blank=True, default='')
    repo_url = models.CharField(max_length=100, unique=True, verbose_name='项目仓库路径')
    repo_model = models.CharField(max_length=10, choices=repo_models, verbose_name='版本控制类型', default='branch')
    src_dir = models.CharField(max_length=100, verbose_name='代码检出目录')
    exclude = models.TextField(blank=True, verbose_name='排除文件', default='')
    run_user = models.CharField(max_length=10, verbose_name='运行服务用户', default='root')
    deploy_webroot = models.CharField(max_length=100, verbose_name='目标机器webroot')
    deploy_releases = models.CharField(max_length=100, verbose_name='目标机器版本库地址')
    releases_num = models.PositiveSmallIntegerField(verbose_name='版本保留个数', default=20)
    prev_deploy = models.TextField(blank=True, verbose_name='代码检出前操作', default='')
    post_deploy = models.TextField(blank=True, verbose_name='代码检出后操作', default='')
    prev_release = models.TextField(blank=True, verbose_name='切换版本前操作', default='')
    post_release = models.TextField(blank=True, verbose_name='切换版本后操作', default='')
    versions = models.TextField(blank=True, verbose_name='存储部署过的版本', default='')

    class Meta:
        db_table = 'ops_project_config'
        verbose_name = '项目配置表'
        verbose_name_plural = '项目配置表'

class Project_Config_Ticket(models.Model):

    proj_name = models.ForeignKey('assets.ProjectName', on_delete=models.CASCADE, verbose_name='项目名称')
    proj_env = models.ForeignKey('assets.ProjectEnv', on_delete=models.CASCADE, verbose_name='项目环境')
    proj_app = models.ForeignKey('assets.ProjectApp', on_delete=models.CASCADE, verbose_name='应用名称')
    proj_audit_group = models.SmallIntegerField(verbose_name='项目授权组', blank=True, null=True, default=None)
    proj_role = models.ForeignKey('ProjectConfig', on_delete=models.CASCADE, verbose_name='项目角色')
    proj_branch_tag = models.CharField(max_length=20, blank=False,null=False, verbose_name='项目分支或Tag')
    proj_uuid = models.UUIDField(default=uuid.uuid4)
    proj_status = models.SmallIntegerField(verbose_name='是否可用', default=0)
    proj_memo = models.CharField(max_length=20, blank=True,null=True, verbose_name='备注')
    wx_notice = models.BooleanField(blank=True, verbose_name='是否开启微信通知', default=False)
    mail_notice = models.BooleanField(blank=True, verbose_name='是否开启郵件通知', default=False)
    to_mail = models.TextField(blank=True, default='', verbose_name='收件人邮箱')
    cc_mail = models.TextField(blank=True, default='', verbose_name='抄送人邮箱')
    versions = models.TextField(blank=True, verbose_name='存储部署过的版本', default='')

    class Meta:
        db_table = 'ops_project_config_ticket'
        unique_together = ("proj_name", "proj_env", "proj_app")
        verbose_name = '配置发布工單表'
        verbose_name_plural = '配置发布工單表'


class Project_Deploy_Ticket(models.Model):  #工单记录表
    STATUS = (
        (0, '已通过'),
        (1, '已拒绝'),
        (2, '审核中'),
        (3, '已部署'),
        (4, '已回滚'),
    )
    LEVEL = (
        (0, '非紧急'),
        (1, '紧急'),
    )
    ticket_no = models.BigIntegerField(verbose_name='发布项目ID',null=False)
    ticket_user = models.CharField(max_length=30, verbose_name='工单申请人')
    ticket_platform = models.ManyToManyField("assets.platformname", related_name='deploy_platform',blank=False, verbose_name='发布平台')
    ticket_config = models.ForeignKey("Project_Config_Ticket",related_name='config_ticket', on_delete=models.CASCADE, blank=False, verbose_name='关联工单配置表')
    ticket_commit = models.CharField(max_length=100, verbose_name='commit ID')
    ticket_subject = models.CharField(max_length=200, verbose_name='工单申请主题')
    ticket_content = models.TextField(verbose_name='工单申请内容')
    ticket_audit = models.CharField(max_length=30, verbose_name='部署指派人')
    ticket_status = models.IntegerField(choices=STATUS, default='审核中', verbose_name='工单状态')
    ticket_level = models.IntegerField(choices=LEVEL, default='非紧急', verbose_name='工单紧急程度')
    ticket_cancel = models.TextField(blank=True, null=True, verbose_name='取消原因')
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='工单创建时间')
    modify_time = models.DateTimeField(auto_now=True, blank=True, verbose_name='工单最后修改时间')
    '''自定义权限'''

    class Meta:
        db_table = 'ops_project_deploy_ticket'
        unique_together = ("ticket_no", "ticket_config", "ticket_commit")
        verbose_name = '部署工单表'
        verbose_name_plural = '部署工单表'


class Project_Deploy_Record(models.Model):
    STATUS = (
        (0, '发布失败'),
        (1, '连接成功'),
        (2, '备份成功'),
        (3, '代码同步'),
        (4, '更改属主'),
        (5, '部署前任务'),
        (6, '部署代码'),
        (9, '部署后任务'),
    )
    assets = models.ForeignKey("assets.Assets", related_name='assets_deploy_record', on_delete=models.DO_NOTHING, blank=False, verbose_name='关联资产记录表')
    deploy_ip = models.GenericIPAddressField(verbose_name='发布IP=资产ID')
    deploy_status = models.IntegerField(choices=STATUS, default=0,verbose_name='发布状态', null=False)
    deploy_times = models.IntegerField(verbose_name='发布次数', default=0, null=False)
    rollback_status = models.IntegerField(default=0,verbose_name='回滚状态', null=False)
    rollback_times = models.IntegerField(verbose_name='回滚次数', default=0, null=False)
    d_ticket_id = models.ForeignKey("Project_Deploy_Ticket", related_name='deploy_ticket', on_delete=models.DO_NOTHING, blank=False, verbose_name='关联工单记录表')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ops_project_deploy_record'
        unique_together = ("deploy_ip", "d_ticket_id")
        verbose_name = '发布记录'
        verbose_name_plural = '发布记录'


class DeployLog(models.Model):
    """部署记录表"""
    d_types = (
        ('deploy', '部署'),
        ('rollback', '回滚')
    )
    project_config = models.ForeignKey('ProjectConfig', on_delete=models.CASCADE)
    deploy_user = models.ForeignKey('users.UserProfile', on_delete=models.CASCADE)
    d_type = models.CharField(max_length=10, choices=d_types, verbose_name='操作类型', default=0)
    branch_tag = models.CharField(max_length=16, verbose_name='分支或标签名称', default='master')
    release_name = models.CharField(max_length=100, verbose_name='部署版本')
    release_desc = models.CharField(max_length=100, verbose_name='版本说明')
    result = models.TextField(verbose_name='部署过程')
    c_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'ops_deploy_log'
        verbose_name = '部署记录表'
        verbose_name_plural = '部署记录表'


class Service(models.Model):
    """服务类型表"""
    project = models.ForeignKey('assets.ProjectName', on_delete=models.CASCADE)
    service_name = models.CharField(max_length=32, verbose_name='服务名称', help_text='数据库、中间件等')
    service_asset = models.ForeignKey('assets.Assets', verbose_name='提供服务的机器', on_delete=models.CASCADE)
    service_memo = models.TextField(blank=True, verbose_name='服务描述', default='')

    class Meta:
        db_table = 'ops_service'
        verbose_name = '服务类型表'
        verbose_name_plural = '服务类型表'
        unique_together = ("service_name","service_asset")
