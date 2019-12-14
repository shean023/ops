import os
import json, time
from collections import deque
from django.conf import settings
from projs.tasks import deploy_log
from conf.logger import deploy_logger
from projs.models import Project_Deploy_Ticket
from assets.models import Assets
from projs.models import Project_Deploy_Record
from utils.db.redis_ops import RedisOps
from projs.utils.git_tools import GitTools
from projs.utils.svn_tools import SVNTools
from ansible.plugins.callback import CallbackBase
from task.utils import ansible_api_v2, gen_resource
from channels.generic.websocket import WebsocketConsumer
from projs.utils.deploy_notice import deploy_mail, deploy_wx


class TicketDeployConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super(TicketDeployConsumer, self).__init__(*args, **kwargs)
        self.redis_instance = RedisOps(settings.REDIS_HOST, settings.REDIS_PORT, 5)
        self.deploy_results = []
        self.host_fail = []
        self.config = None
        self.d_type = None
        self.release_name = None
        self.release_desc = None
        self.host_list = None
        self.branch_tag = None

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):

        # {"tid": "19", "pid": "3", "dserver": ["2", "3"], "d_type": "deploy"}　
        info = json.loads(text_data)
        self.config = Project_Deploy_Ticket.objects.get(id=info.get('tid'))

        unique_key = self.config.ticket_config.proj_uuid
        self.d_type = info.get('d_type').capitalize()

        step_msg = "[{} " "{}] <font size=\"2\" color=\"blue\">{}</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})
        ok_msg = "[{} " "{}] <font size=\"2\" color=\"blue\">{}...OK</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})
        fail_msg = "[{} " "{}] <font size=\"2\" color=\"color: #FF0000\">{}...Error</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})
        warn_msg = "[{} " "{}] <font size=\"2\" color=\"orange\">{}...warning</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})

        if self.redis_instance.get(unique_key):
            self.send_save(fail_msg.format("有相同的任务正在进行，请稍后重试！"))
            self.close()
        else:
            self.redis_instance.set(unique_key, 1)
            ticket_no = self.config.ticket_no
            if self.d_type == 'Deploy':

                self.branch_tag = self.config.ticket_config.proj_branch_tag
                commit = self.config.ticket_commit
                self.release_name = commit if commit else self.branch_tag

                if self.config.ticket_config.proj_role.repo == 'git':
                    tool = GitTools(repo_url=self.config.ticket_config.proj_role.repo_url,
                                    path=self.config.ticket_config.proj_role.src_dir,
                                    env=self.config.ticket_config.proj_env.projenv_name)
                    try:
                        tool.checkout(self.branch_tag)
                        self.send_save(ok_msg.format("切换分支：" + self.branch_tag))
                        if commit:
                            self.send_save(ok_msg.format("Commit ID：" + commit[:7]))
                            tool.checkout(commit)
                            self.release_desc = tool.get_commit_msg(self.branch_tag, commit)
                        else:
                            self.release_desc = self.release_name
                        self.send_save(ok_msg.format("Commit Msg: " + self.release_desc))
                    except Exception as e:
                        self.send_save(fail_msg("检出代码"), close=True)

                    self.deploy(ticket_no, info, tool, step_msg, ok_msg, fail_msg, warn_msg)

                elif self.config.ticket_config.proj_role.repo == 'svn':
                    tool = SVNTools(repo_url=self.config.ticket_config.proj_role.repo_url,
                                    path=self.config.ticket_config.proj_role.src_dir,
                                    env=self.config.ticket_config.proj_env.projenv_name,
                                    username=self.config.ticket_config.proj_role.repo_user,
                                    password=self.config.ticket_config.proj_role.repo_password)
                    self.send_save(step_msg.format("【检出SVN代码】"))
                    if commit:
                        self.send_save(ok_msg.format("Commit ID： " + commit[:7]))
                        model_name = '' if self.config.ticket_config.proj_role.repo_model == 'trunk' else self.brahch_tag
                        self.release_desc = tool.get_commit_msg(int(commit),
                                                                self.config.ticket_config.proj_role.repo_model,
                                                                model_name=model_name)
                    else:
                        self.release_desc = self.release_name
                    self.send_save(ok_msg.format("Commit Msg: " + self.release_desc))

                    c = int(commit) if commit else None

                    # 执行检出代码之前的命令，比如安装依赖等
                    if self.config.ticket_config.proj_role.prev_deploy:
                        try:
                            code = tool.run_cmd(self.config.ticket_config.proj_role.prev_deploy)
                            if code == 0:
                                self.send_save(ok_msg.format("执行检出代码之前的命令"))
                            else:
                                self.send_save(fail_msg("执行检出代码之前的命令"), close=True)
                        except Exception as e:
                            self.send_save(fail_msg("执行检出代码之前的命令"), close=True)

                    # 执行检出代码任务
                    try:
                        if self.config.ticket_config.proj_role.repo_model == 'trunk':
                            tool.checkout(self.config.ticket_config.proj_role.repo_model, revision=c)
                            self.send_save(ok_msg.format("检出代码Trunk版本号: " + c))
                        else:
                            tool.checkout(self.config.ticket_config.proj_role.repo_model, self.branch_tag,
                                          revision=commit)
                            self.send_save(ok_msg.format("检出分支： " + self.branch_tag + "版本号： "))
                    except Exception as e:
                        self.send_save(fail_msg("执行检出"), close=True)

                    self.deploy(ticket_no, info, tool, step_msg, ok_msg, fail_msg, warn_msg)

                self.close()
                self.redis_instance.delete(unique_key)

            elif self.d_type == 'Rollback':
                if self.config.ticket_config.proj_role.repo == 'git':
                    tool = GitTools(repo_url=self.config.ticket_config.proj_role.repo_url,
                                    path=self.config.ticket_config.proj_role.src_dir,
                                    env=self.config.ticket_config.proj_env.projenv_name)
                    self.deploy(ticket_no, info, tool, step_msg, ok_msg, fail_msg, warn_msg)
                elif self.config.ticket_config.proj_role.repo == 'svn':
                    tool = SVNTools(repo_url=self.config.ticket_config.proj_role.repo_url,
                                    path=self.config.ticket_config.proj_role.src_dir,
                                    env=self.config.ticket_config.proj_env.projenv_name,
                                    username=self.config.ticket_config.proj_role.repo_user,
                                    password=self.config.ticket_config.proj_role.repo_password)
                    self.deploy(ticket_no, info, tool, step_msg, ok_msg, fail_msg, warn_msg)
                else:
                    pass
            elif self.d_type == 'Dcheck':
                self.deploy_check(ok_msg)
            else:
                pass

    def deploy_check(self, ok_msg):
        count = 0
        for pid in self.config.ticket_platform.all():
            for ser in Assets.objects.filter(asset_projenv=self.config.ticket_config.proj_env.id).filter(
                    asset_platform=pid).filter(asset_projapp__id=self.config.ticket_config.proj_app.id):
                dt = Project_Deploy_Record.objects.filter(deploy_ip=ser.asset_management_ip,
                                                          d_ticket_id=self.config.id)
                if dt.count() == 0:
                    self.send_save(ok_msg.format("{}: {} {} {} 【无发布记录】").format(
                        pid.platform_name, ser.asset_management_ip, ser.asset_hostname,
                        'Available' if ser.asset_status == 0 else "Inactive"))
                    if ser.asset_status == 0:
                        count += 1
                else:
                    self.send_save(ok_msg.format("{}: {} {} {} {} {} {} {}").format(
                        pid.platform_name, ser.asset_management_ip, ser.asset_hostname,
                        'Available' if ser.asset_status == 0 else "Inactive", '【发布成功】' if dt[0].deploy_status == 9 else "【发布失败】",
                        dt[0].deploy_times, '【回滚成功】' if dt[0].rollback_status == 1 else 'None',
                        'None' if dt[0].rollback_times == 0 else dt[0].rollback_times))
                    if dt[0].deploy_status != 9:
                        count += 1
        self.send_save(ok_msg.format("Deploy Check Finished！ Count: {}").format(count), close=True)

    def disconnect(self, close_code):
        self.send_save("def disconnect:")

    def deploy(self, ticket_no, info, tool, step_msg, ok_msg, fail_msg, warn_msg):

        host_ids = info.get('dserver')  # 这里检测发布（回滚）服务器
        tid = Project_Deploy_Ticket.objects.get(id=info.get('tid'))
        dsList = []
        for hs in host_ids:
            ds = Assets.objects.get(id=hs)
            dt = Project_Deploy_Record.objects.filter(deploy_ip=ds.asset_management_ip,
                                                      d_ticket_id=info.get('tid'))

            if dt.count() == 1:  # 是否有发布记录：有
                if self.d_type == "Rollback":  # 不要移动这个代码段位置，否则会逻辑错误！必需要先判断是否是回滚
                    if dt[0].rollback_times != dt[0].deploy_times:
                        self.send_save(ok_msg.format("{ip} {hs} 第{times}次回滚").format(
                            ip=ds.asset_management_ip,
                            hs=ds.asset_hostname,
                            times=dt[0].rollback_times + 1,
                        ))
                        try:  # 回滚次数+1
                            dsList.append(hs)
                            dt.update(rollback_times=dt[0].rollback_times + 1,
                                      update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                        except Exception as e:
                            self.send_save(fail_msg.format("更新 rollback_times + 1 回滚次数异常！{}").format(e))
                    else:
                        self.send_save(fail_msg.format("回滚次数不能大于发布次数！"))
                elif dt[0].deploy_status == 9:  # 判断记录是否发布成功：发布成功

                    if self.d_type == "Deploy":
                        self.send_save(
                            warn_msg.format("{ip} {hs} 发布记录为成功，请勿重复发布,踢出发布列表！").format(ip=ds.asset_management_ip,
                                                                                       hs=ds.asset_hostname if ds.asset_hostname else 'null'))
                        if dt[0].deploy_times == 1:
                            self.send_save(
                                warn_msg.format("{ip} {hs} 回滚记录为成功，请确认部署状态！").format(ip=ds.asset_management_ip,
                                                                                     hs=ds.asset_hostname if ds.asset_hostname else 'null'))

                elif dt[0].deploy_status < 9:  # 判断记录是否发布成功:没有发成功
                    if self.d_type == 'Deploy':
                        self.send_save(ok_msg.format("{ip} {hs} 第{times}次发布 Start").format(
                            ip=ds.asset_management_ip,
                            hs=ds.asset_hostname,
                            times=dt[0].deploy_times + 1,
                        ))
                        try:  # 发布次数+1
                            dsList.append(hs)
                            dt.update(deploy_times=dt[0].deploy_times + 1,
                                      update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                        except Exception as e:
                            self.send_save(fail_msg.format("更新 deploy_times + 1 发布次数异常！{}").format(e))

            elif dt.count() == 0:  # 是否有发布记录：无

                if self.d_type == 'Deploy':
                    self.send_save(ok_msg.format("{ip} {hs} 第1次发布 Start").format(
                        ip=ds.asset_management_ip,
                        hs=ds.asset_hostname if ds.asset_hostname else 'null'
                    ))

                    try:  # 创建发布记录表
                        dtc = Project_Deploy_Record.objects.create(deploy_ip=ds.asset_management_ip,
                                                                   deploy_times=1,
                                                                   d_ticket_id=tid,
                                                                   )
                        dsList.append(hs)
                    except Exception as e:
                        self.send_save(fail_msg.format("创建发布记录表异常! {}").format(e))
                        return

                elif self.d_type == 'Rollback':
                    self.send_save(fail_msg.format("{} 没有发布记录，回滚终止！").format(ds.asset_management_ip))
                else:
                    pass

        if dsList:
            resource = gen_resource.GenResource().gen_host_list(host_ids=dsList)
            self.host_list = [server['ip'] for server in resource]
            ans = ansible_api_v2.ANSRunner(resource, sock=self)
        else:
            self.send_save(fail_msg.format("没有发布(回滚)主机，部署终止！"), close=True)
            return

        if self.d_type == 'Deploy':
            # 执行同步代码之前的命令，比如编译等
            if self.config.ticket_config.proj_role.post_deploy:
                try:
                    code = tool.run_cmd(self.config.ticket_config.proj_role.post_deploy)
                    if code == 0:
                        self.send_save(ok_msg.format("执行同步代码之前的命令成功"))
                    else:
                        self.send_save(fail_msg.format("执行同步代码之前的命令失败"))
                        return
                except Exception as e:
                    self.send_save(fail_msg.format("执行同步代码之前的命令异常! {}").format(e))
                    return

            # 检测目标机器是否连通，如果连通，判断是否存在存储代码版本的路径，如果不存在就创建
            ans.run_module(self.host_list, module_name='file', module_args='path={} state=directory'.format(
                os.path.join(self.config.ticket_config.proj_role.deploy_releases, tool.proj_name)), deploy=True,
                           d_type=self.d_type, task='connet', tid=tid.id)

            # 备份代码目录
            try:
                backup_dir = self.gen_dir(tool, ticket_no, backup="backup") + "/" + time.strftime("%Y%m%d%H%M%S")
                backup_dest = os.path.join(self.config.ticket_config.proj_role.deploy_webroot, tool.proj_name)
                ans.run_module(self.host_list, module_name='shell',
                               module_args='mkdir -p {} && /bin/cp -rf {}/* {}'.format(backup_dir, backup_dest,
                                                                                       backup_dir), deploy=True,
                               d_type=self.d_type, task="backup", tid=tid.id)
            except Exception as e:
                self.send_save(fail_msg.format("目标服务器备份代码异常: {}").format(e))
                return

            # 将代码同步至目标服务器
            try:
                # /data/version/urlmonitor/123131232121238
                des_dir = self.gen_dir(tool, ticket_no)
                # 通过判断路径中是否存在target目录确定是否是JAVA项目
                # target_path /data/urlmonitor/UAT/target
                target_path = os.path.join(tool.proj_path, 'target')
                java_proj = os.path.exists(target_path)
                if java_proj:
                    self.send_save(ok_msg.format("是JAVA项目"))
                else:
                    self.send_save(ok_msg.format("非JAVA项目"))

                # 代码同步源目录
                src_dir = '{}/{}/'.format(target_path, tool.proj_name) if os.path.exists(
                    target_path) else tool.proj_path + '/'
                self.sync_code(ans, self.host_list, src_dir, des_dir,
                               excludes=self.config.ticket_config.proj_role.exclude, d_type=self.d_type,
                               task="sync_code", tid=tid.id)

                # 如果运行服务的用户不是root，就将代码目录的属主改为指定的user
                if self.config.ticket_config.proj_role.run_user != 'root':
                    ans.run_module(self.host_list, module_name='file',
                                   module_args='path={} owner={} recurse=yes'.format(des_dir,
                                                                                     self.config.ticket_config.proj_role.run_user),
                                   deploy=True, send_msg=False, d_type=self.d_type, task="owner", tid=tid.id)
            except Exception as e:
                self.send_save(fail_msg.format("代码同步至目标服务器异常 {}").format(e))
                return

            # 执行部署前任务
            if self.config.ticket_config.proj_role.prev_release:
                try:
                    self.run_cmds(ans, self.host_list, self.config.ticket_config.proj_role.prev_release,
                                  d_type=self.d_type, task="prev_release", tid=tid.id)
                except Exception as e:
                    self.send_save(fail_msg.format("目标服务器部署前任务异常 {}").format(e))

            # 配置软连接，指向指定的版本目录
            try:
                src = self.gen_dir(tool, ticket_no)
                dest = os.path.join(self.config.ticket_config.proj_role.deploy_webroot, tool.proj_name)
                ans.run_module(self.host_list, module_name='shell',
                               module_args='rm -rf {} && ln -sf {} {}'.format(dest, src + '/', dest), deploy=True,
                               d_type=self.d_type, task="release", tid=tid.id)
            except Exception as e:
                self.send_save(fail_msg.format("目标服务器部署异常 {}").format(e))

            # 执行部署后任务
            if self.config.ticket_config.proj_role.post_release:
                try:
                    self.run_cmds(ans, self.host_list, self.config.ticket_config.proj_role.post_release,
                                  d_type=self.d_type, task='post_release', tid=tid.id)
                except Exception as e:
                    self.send_save(fail_msg.format("目标服务器部署后任务异常 {}").format(e))

        elif self.d_type == 'Rollback':
            self.send_save(ok_msg.format("开始回滚！"))
            # 回滚代码
            try:
                backup_dir = self.gen_dir(tool, ticket_no, backup="backup")
                backup_dest = os.path.join(self.config.ticket_config.proj_role.deploy_webroot, tool.proj_name)
                print(backup_dir, backup_dest)
                ans.run_module(self.host_list, module_name='raw',
                               module_args='cd {bak_dir} && back_dir\=`ls -lt |egrep \^d|egrep -v rollback\$|cut -d " " -f 9|egrep \^[2][0-9]|head -n 1` &&  mv $back_dir $back_dir.rollback  && rm -rf {bak_dest} && ln -sf {bak_dir}/$back_dir.rollback {bak_dest}'.format(
                                   bak_dir=backup_dir, bak_dest=backup_dest, ), deploy=True, d_type=self.d_type,
                               task="rollback", tid=tid.id)
            except Exception as e:
                self.send_save(fail_msg.format("目标服务器回滚代码异常: {}").format(e))
                return

    @staticmethod
    def sync_code(ans, host_list, src_dir, des_dir, excludes=None, d_type=None, task=None, tid=None):
        d_type = d_type
        task = task
        tid = tid
        if excludes:
            opts = ''
            for i in excludes.split('\n'):
                if i.startswith('#'):
                    continue
                opts += ',--exclude=' + i
            opts = opts.lstrip(',')
            ans.run_module(host_list, module_name='synchronize',
                           module_args='src={} dest={} delete=yes rsync_opts="{}"'.format(src_dir, des_dir, opts),
                           deploy=True, d_type=d_type, task=task)
        else:
            ans.run_module(host_list, module_name='synchronize',
                           module_args='src={} dest={} delete=yes'.format(src_dir, des_dir), deploy=True, d_type=d_type,
                           task=task, tid=tid)

    @staticmethod
    def run_cmds(ans, host_list, cmds, d_type=None, task=None, tid=None):
        d_type = d_type
        task = task
        tid = tid
        c = ''
        for cmd in cmds.split('\n'):
            if cmd.startswith('#'):
                continue
            c += cmd + ' && '
        c = c.rstrip(' && ')
        ans.run_module(host_list, module_name='shell', module_args=c, deploy=True, d_type=d_type, task=task, tid=tid)

    def gen_dir(self, tool, ticket_no, backup=None):
        ticket_no = ticket_no
        backup = backup
        if backup:
            des_dir = os.path.join(self.config.ticket_config.proj_role.deploy_releases, tool.proj_name,
                                   backup, '{}'.format(ticket_no))
        else:
            des_dir = os.path.join(self.config.ticket_config.proj_role.deploy_releases, tool.proj_name,
                                   '{}'.format(ticket_no))
        return des_dir

    @staticmethod
    def del_release(ans, host_list, path, dir_name):
        """按照数据库设置的保留版本个数，删除最早的多余的版本"""
        ans.run_module(host_list, module_name='shell',
                       module_args='cd {path} && rm -rf {dir_name}'.format(path=path, dir_name=dir_name), deploy=True,
                       send_msg=False)

    def send_save(self, msg, close=False, send=True):
        if send:
            self.send(msg, close=close)
            self.deploy_results.append(msg)


class DeployResultsCollector(CallbackBase):
    """
    直接执行模块命令的回调类
    """

    def __init__(self, sock, send_msg, d_type, task, tid, *args, **kwargs):
        super(DeployResultsCollector, self).__init__(*args, **kwargs)
        self.sock = sock
        self.send_msg = send_msg
        self.d_type = d_type
        self.task = task
        self.tid = tid
        step_msg = "[{} " "{}] <font size=\"2\" color=\"blue\">{}</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})
        self.ok_msg = "[{} " "{}] <font size=\"2\" color=\"blue\">{}...OK</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})
        self.fail_msg = "[{} " "{}] <font size=\"2\" color=\"color: #FF0000\">{}...Error</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})
        warn_msg = "[{} " "{}] <font size=\"2\" color=\"orange\">{}...warning</font></br>".format(
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), self.d_type, {})

    def v2_runner_on_unreachable(self, result):
        if 'msg' in result._result:
            data = '主机{host}不可达！==> {stdout}\n剔除该主机！\n'.format(
                host=result._host.name, stdout=result._result.get('msg'))
        else:
            data = '主机{host}不可达！==> {stdout}\n剔除该主机！\n'.format(
                host=result._host.name, stdout=json.dumps(result._result, indent=4))

        self.chk_host_list(data, result._host.name)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        dt = Project_Deploy_Record.objects.filter(deploy_ip=result._host.name, d_ticket_id=self.tid)

        if self.task == 'connet':
            self.sock.send_save(self.ok_msg.format("{} 连接成功").format(result._host.name))
            if len(dt) and dt[0].deploy_status == 0:
                dt.update(deploy_status=1, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif self.task == 'backup':
            self.sock.send_save(self.ok_msg.format("{} 代码同步至目标服务器").format(result._host.name))
            if len(dt) and dt[0].deploy_status == 1:
                dt.update(deploy_status=2, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif self.task == 'sync_code':
            self.sock.send_save(self.ok_msg.format("{} 代码同步至目标服务器").format(result._host.name))
            if len(dt) and dt[0].deploy_status == 2:
                dt.update(deploy_status=3, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif self.task == 'owner':
            self.sock.send_save(self.ok_msg.format("{} 更改目标服务器文件夹属主").format(result._host.name))
            if len(dt) and dt[0].deploy_status == 3:
                dt.update(deploy_status=4, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif self.task == 'prev_release':
            self.sock.send_save(self.ok_msg.format("{} 目标服务器部署前任务").format(result._host.name))
            if len(dt) and dt[0].deploy_status == 4:
                dt.update(deploy_status=5, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif self.task == 'release':
            self.sock.send_save(self.ok_msg.format("{} 目标服务器部署代码").format(result._host.name))
            if len(dt) and dt[0].deploy_status == 5:
                dt.update(deploy_status=6, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif self.task == 'post_release':
            self.sock.send_save(self.ok_msg.format("{} 目标服务器部署后任务").format(result._host.name))
            if len(dt) and dt[0].deploy_status == 6:
                dt.update(deploy_status=9, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        elif self.task == 'rollback':
            self.sock.send_save(self.ok_msg.format("{} 回滚完成").format(result._host.name))
            if len(dt):
                dt.update(rollback_status=1, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        else:
            self.sock.send_save(self.ok_msg.format("{}").format(result._host.name))

            # try:  # 发布成功,更新字段deploy_status=1
            #     dt.update(deploy_status=1, update_date=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            # except Exception as e:
            #     self.send_save(fail_msg.format("更新 deploy_status=1 发布状态异常！{}").format(e))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        if 'stderr' in result._result:
            data = '主机{host}执行任务失败 ==> {stdout}\n剔除该主机！'.format(
                host=result._host.name, stdout=result._result.get('stderr').encode().decode('utf-8'))
        elif 'msg' in result._result:
            data = '主机{host}执行任务失败 ==> {stdout}\n剔除该主机！'.format(
                host=result._host.name, stdout=result._result.get('msg'))
        else:
            data = '主机{host}执行任务失败 ==> {stdout}\n剔除该主机！'.format(
                host=result._host.name, stdout=json.dumps(result._result, indent=4))
        self.chk_host_list(data, result._host.name)

    def chk_host_list(self, data, host):
        if self.task == 'connet':
            self.sock.send_save(self.fail_msg.format("{} 连接失败").format(data))
        elif self.task == 'backup':
            self.sock.send_save(self.fail_msg.format("{} 目标服务器备份代码失败").format(data))
        elif self.task == 'sync_code':
            self.sock.send_save(self.fail_msg.format("{} 代码同步至目标服务器失败").format(data))
        elif self.task == 'owner':
            self.sock.send_save(self.fail_msg.format("{} 更改目标服务器文件夹属主失败").format(data))
        elif self.task == 'prev_release':
            self.sock.send_save(self.fail_msg.format("{} 目标服务器部署前任务失败").format(data))
        elif self.task == 'release':
            self.sock.send_save(self.fail_msg.format("{} 目标服务器部署代码失败").format(data))
        elif self.task == 'post_release':
            self.sock.send_save(self.fail_msg.format("{} 目标服务器部署后任务失败").format(data))
        elif self.task == 'rollback':
            self.sock.send_save(self.fail_msg.format("{} 回滚代码失败").format(data))
        else:
            self.sock.send_save(self.fail_msg.format("{}　任务失败").format(data))

        self.sock.host_list.remove(host)
        self.sock.host_fail.append(host)
        if len(self.sock.host_list) == 0:
            self.sock.send_save(self.fail_msg.format("所有主机均部署失败，退出部署流程！"), close=True)
            self.sock.deploy_results.append('<p style="color: #FF0000">所有主机均部署失败！退出部署流程！</p>')
