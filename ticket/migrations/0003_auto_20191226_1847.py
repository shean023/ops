# Generated by Django 2.0.5 on 2019-12-26 10:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ticket', '0002_auto_20191226_1839'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketAuditModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='执行人（可以配置负数表示自动执行）')),
                ('order', models.SmallIntegerField(verbose_name='执行顺序')),
            ],
            options={
                'verbose_name': '执行流程表',
                'verbose_name_plural': '执行流程',
                'db_table': 'ops_ticket_auditmodel',
            },
        ),
        migrations.CreateModel(
            name='TicketExecModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(verbose_name='执行人（可以配置负数表示自动执行）')),
                ('order', models.SmallIntegerField(verbose_name='执行顺序')),
            ],
            options={
                'verbose_name': '执行流程表',
                'verbose_name_plural': '执行流程',
                'db_table': 'ops_ticket_execmodel',
            },
        ),
        migrations.CreateModel(
            name='TictetType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='工单类型名称')),
                ('confirm_duration', models.IntegerField(default='30', verbose_name='默认确认时长（分）')),
                ('exec_duration', models.IntegerField(default='30', verbose_name='默认执行时长（分）')),
                ('effective_date', models.IntegerField(default='5', verbose_name='默认有效期（天）')),
                ('type_form', models.CharField(max_length=64, verbose_name='工单类型表单')),
                ('ctime', models.DateTimeField(auto_now_add=True, null=True, verbose_name='工单类型创建时间')),
                ('mtime', models.DateTimeField(auto_now=True, verbose_name='工单类型最后修改时间')),
                ('status', models.IntegerField(choices=[(1, '启用'), (2, '禁用'), (3, '删除')], default='1', verbose_name='工单状态')),
                ('createuser_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tt_create', to=settings.AUTH_USER_MODEL, verbose_name='工单类型创建人')),
            ],
            options={
                'verbose_name': '工单类型表',
                'verbose_name_plural': '工单类型表：创建工单执行流程和审核流程及工单响应时间',
                'db_table': 'ops_ticket_type',
                'permissions': (('ticket_type_read', '读取工单类型权限'), ('ticket_type_write', '写入工单类型权限')),
            },
        ),
        migrations.AddField(
            model_name='ticketexecmodel',
            name='tt_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exec_model', to='ticket.TictetType', verbose_name='工单类型表'),
        ),
        migrations.AddField(
            model_name='ticketauditmodel',
            name='tt_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_model', to='ticket.TictetType', verbose_name='工单类型表'),
        ),
        migrations.AlterUniqueTogether(
            name='tictettype',
            unique_together={('name', 'type_form')},
        ),
    ]
