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
    #deploy_server = models.ManyToManyField('assets.ServerAssets', verbose_name='目标部署机器')
    deploy_webroot = models.CharField(max_length=100, verbose_name='目标机器webroot')
    deploy_releases = models.CharField(max_length=100, verbose_name='目标机器版本库地址')
    releases_num = models.PositiveSmallIntegerField(verbose_name='版本保留个数', default=20)
    prev_deploy = models.TextField(blank=True, verbose_name='代码检出前操作', default='')
    post_deploy = models.TextField(blank=True, verbose_name='代码检出后操作', default='')
    prev_release = models.TextField(blank=True, verbose_name='切换版本前操作', default='')
    post_release = models.TextField(blank=True, verbose_name='切换版本后操作', default='')
    versions = models.TextField(blank=True, verbose_name='存储部署过的版本', default='')
    #wx_notice = models.BooleanField(blank=True, verbose_name='是否开启微信通知', default=False)
    #to_mail = models.TextField(blank=True, default='', verbose_name='收件人邮箱')
    #cc_mail = models.TextField(blank=True, default='', verbose_name='抄送人邮箱')

    class Meta:
        db_table = 'ops_project_config'
        verbose_name = '项目配置表'
        verbose_name_plural = '项目配置表'

class Project_Config_Ticket(models.Model):

    proj_name = models.SmallIntegerField(verbose_name='项目名称')
    proj_env = models.SmallIntegerField(verbose_name='项目环境')
    proj_audit_group = models.SmallIntegerField(verbose_name='项目授权组', blank=True, null=True, default=None)
    proj_role = models.ForeignKey('ProjectConfig', on_delete=models.CASCADE, verbose_name='项目角色')
    proj_uuid = models.UUIDField(default=uuid.uuid4)
    proj_status = models.SmallIntegerField(verbose_name='是否可用', default=0)
    proj_memo = models.CharField(max_length=20, blank=True,null=True, verbose_name='备注')
    wx_notice = models.BooleanField(blank=True, verbose_name='是否开启微信通知', default=False)
    mail_notice = models.BooleanField(blank=True, verbose_name='是否开启郵件通知', default=False)
    to_mail = models.TextField(blank=True, default='', verbose_name='收件人邮箱')
    cc_mail = models.TextField(blank=True, default='', verbose_name='抄送人邮箱')

    class Meta:
        db_table = 'project_config_ticket'
        unique_together = ("proj_name", "proj_env")
        verbose_name = '配置发布工單表'
        verbose_name_plural = '配置发布工單表'
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
