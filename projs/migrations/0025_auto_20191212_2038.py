# Generated by Django 2.0.5 on 2019-12-12 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projs', '0024_auto_20191211_2140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project_deploy_record',
            name='deploy_ip',
            field=models.GenericIPAddressField(verbose_name='发布IP=资产ID'),
        ),
    ]