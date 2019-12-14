# Generated by Django 2.0.5 on 2019-12-10 11:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projs', '0022_auto_20191203_1618'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project_Deploy_Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deploy_ip', models.IntegerField(verbose_name='发布IP=资产ID')),
                ('deploy_status', models.IntegerField(choices=[(0, '发布失败'), (1, '发布成功'), (2, '回滚失败'), (3, '回滚成功')], verbose_name='发布状态')),
                ('deploy_times', models.IntegerField(default=0, verbose_name='发布次数')),
                ('rollback_times', models.IntegerField(default=0, verbose_name='回滚次数')),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '发布记录',
                'verbose_name_plural': '发布记录',
                'db_table': 'ops_project_deploy_record',
            },
        ),
        migrations.AlterModelOptions(
            name='project_deploy_ticket',
            options={'verbose_name': '部署工单表', 'verbose_name_plural': '部署工单表'},
        ),
        migrations.AlterField(
            model_name='project_deploy_ticket',
            name='ticket_config',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='config_ticket', to='projs.Project_Config_Ticket', verbose_name='关联工单配置表'),
        ),
        migrations.AddField(
            model_name='project_deploy_record',
            name='d_ticket_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deploy_ticket', to='projs.Project_Deploy_Ticket', verbose_name='关联工单记录表'),
        ),
    ]