# Generated by Django 2.0.12 on 2020-01-09 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20200109_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='department_id',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_dep', to='users.Department', verbose_name='所属部门'),
        ),
    ]
