# Generated by Django 2.0.5 on 2019-12-13 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projs', '0028_auto_20191212_2116'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectconfig',
            name='versions',
        ),
        migrations.AddField(
            model_name='project_config_ticket',
            name='versions',
            field=models.TextField(blank=True, default='', verbose_name='存储部署过的版本'),
        ),
        migrations.AlterField(
            model_name='project_deploy_record',
            name='deploy_status',
            field=models.IntegerField(choices=[(0, '发布失败'), (1, '连接成功'), (2, '备份成功'), (3, '代码同步'), (4, '更改属主'), (5, '部署前任务'), (6, '部署代码'), (9, '部署后任务')], default=0, verbose_name='发布状态'),
        ),
    ]