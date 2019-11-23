# Generated by Django 2.0.5 on 2019-11-21 08:45

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('mobile', models.CharField(blank=True, max_length=11, null=True, verbose_name='手机号码')),
                ('image', models.ImageField(default='images/default.png', upload_to='images/%Y/%m/%d/')),
                ('login_status', models.SmallIntegerField(choices=[(0, '在线'), (1, '离线'), (2, '忙碌'), (3, '离开')], default=1, verbose_name='登录状态')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户表',
                'verbose_name_plural': '用户表',
                'db_table': 'ops_user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='计划标题')),
                ('content', models.TextField(verbose_name='计划内容')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, '未完成'), (1, '已完成')], default=0, verbose_name='任务状态')),
                ('start_time', models.DateTimeField(default='', verbose_name='开始时间')),
                ('end_time', models.DateTimeField(default='', verbose_name='结束时间')),
                ('add_time', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('attention', models.ManyToManyField(blank=True, related_name='attention_user', to=settings.AUTH_USER_MODEL, verbose_name='关注者')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='self_user', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'verbose_name': '日程管理',
                'verbose_name_plural': '日程管理',
                'db_table': 'ops_users_plan',
            },
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_role_name', models.CharField(max_length=32, unique=True, verbose_name='角色名称')),
                ('group_role', models.ManyToManyField(to='auth.Group', verbose_name='组角色')),
                ('u_role', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='用户角色')),
                ('user_role_permissions', models.ManyToManyField(to='auth.Permission', verbose_name='角色拥有权限')),
            ],
            options={
                'verbose_name': '角色管理',
                'verbose_name_plural': '角色管理',
                'db_table': 'ops_user_role',
            },
        ),
        migrations.AlterUniqueTogether(
            name='userplan',
            unique_together={('title', 'user')},
        ),
    ]
