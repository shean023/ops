# -*- coding: utf-8 -*-
from builtins import print

#from confd.models import Project_Confd
from confd.models import Config_Confd, Confd_Detail
from task.models import AnsibleInventory
from rest_framework import serializers
from assets.models import *
from utils.crypt_pwd import CryptPwd
from fort.models import *
from projs.models import *
from django_celery_beat.models import PeriodicTask
from wiki.models import Post
import datetime


class AssetsSerializer(serializers.ModelSerializer):
    asset_management_ip = serializers.IPAddressField(allow_blank=True, allow_null=True)
    class Meta:

        model = Assets
        fields = '__all__'

    def update(self, instance, validated_data):
        asset_projapp = validated_data.get('asset_projapp', None)
        instance.asset_management_ip = validated_data.get('asset_management_ip', None)
        instance.asset_nu = validated_data.get('asset_nu', None)
        instance.asset_model = validated_data.get('asset_model', None)
        instance.asset_status = validated_data.get('asset_status', None)
        instance.asset_system_type = validated_data.get('asset_system_type', None)
        instance.asset_purchase_day = validated_data.get('asset_purchase_day', None)
        instance.asset_expire_day = validated_data.get('asset_expire_day', None)
        instance.asset_price = validated_data.get('asset_price', None)
        instance.asset_provider = validated_data.get('asset_provider', None)
        instance.asset_admin = validated_data.get('asset_admin', None)
        instance.asset_idc = validated_data.get('asset_idc', None)
        instance.asset_cabinet = validated_data.get('asset_cabinet', None)
        instance.asset_platform = validated_data.get('asset_platform', None)
        instance.asset_proj = validated_data.get('asset_proj', None)
        instance.asset_projenv = validated_data.get('asset_projenv', None)
        instance.asset_memo = validated_data.get('asset_memo', None)
        instance.asset_update_time = datetime.datetime.now()

        if asset_projapp:
            instance.asset_projapp.clear()
            instance.asset_projapp.add(*asset_projapp)
            instance.save()
        else:
            instance.asset_projapp.clear()
            instance.save()
        return instance


class ServerAssetsSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(required=False)

    class Meta:
        model = ServerAssets
        fields = '__all__'

    def create(self, data):
        if data.get('assets'):
            assets_data = data.pop('assets')
            if 'asset_projapp' in assets_data:
                asset_projapp = assets_data.pop('asset_projapp')
                assets = Assets.objects.create(**assets_data)
                assets.asset_projapp.add(*asset_projapp)
            else:
                assets = Assets.objects.create(**assets_data)

        else:
            assets = Assets()
        data['assets'] = assets
        data['password'] = CryptPwd().encrypt_pwd(data['password'])
        server = ServerAssets.objects.create(**data)
        return server

class NetworkAssetsSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(many=False, required=False)

    class Meta:
        model = NetworkAssets
        fields = '__all__'

    def create(self, data):
        if data.get('assets'):
            assets_data = data.pop('assets')
            assets = Assets.objects.create(**assets_data)
        else:
            assets = Assets()
        data['assets'] = assets
        network = NetworkAssets.objects.create(**data)
        return network


class OfficeAssetsSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(many=False, required=False)

    class Meta:
        model = OfficeAssets
        fields = '__all__'

    def create(self, data):
        if data.get('assets'):
            assets_data = data.pop('assets')
            assets = Assets.objects.create(**assets_data)
        else:
            assets = Assets()
        data['assets'] = assets
        office = OfficeAssets.objects.create(**data)
        return office


class SecurityAssetsSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(many=False, required=False)

    class Meta:
        model = SecurityAssets
        fields = '__all__'

    def create(self, data):
        if data.get('assets'):
            assets_data = data.pop('assets')
            assets = Assets.objects.create(**assets_data)
        else:
            assets = Assets()
        data['assets'] = assets
        security = SecurityAssets.objects.create(**data)
        return security


class StorageAssetsSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(many=False, required=False)

    class Meta:
        model = StorageAssets
        fields = '__all__'

    def create(self, data):
        if data.get('assets'):
            assets_data = data.pop('assets')
            assets = Assets.objects.create(**assets_data)
        else:
            assets = Assets()
        data['assets'] = assets
        storage = StorageAssets.objects.create(**data)
        return storage


class SoftwareAssetsSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(many=False, required=False)

    class Meta:
        model = SoftwareAssets
        fields = '__all__'

    def create(self, data):
        if data.get('assets'):
            assets_data = data.pop('assets')
            assets = Assets.objects.create(**assets_data)
        else:
            assets = Assets()
        data['assets'] = assets
        software = StorageAssets.objects.create(**data)
        return software


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjenvSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectEnv
        fields = '__all__'


class ProjappSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectApp
        fields = ('id','projectname','projapp_name','projapp_memo')


class ProjnameSerializer(serializers.ModelSerializer):
    projectapp = ProjappSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectName
        fields = ('id', 'projname_name', 'projname_org', 'projname_memo','platformname', 'projectapp')

    def update(self, instance, validated_data):
        platformname = validated_data.get('platformname', None)
        instance.projname_name = validated_data.get('projname_name', None)
        instance.projname_memo= validated_data.get('projname_memo', None)

        if platformname:
            instance.platformname.clear()
            instance.platformname.add(*platformname)
            instance.save()
        else:
            instance.platformname.clear()
            instance.save()
        return instance


class PlatformNameSerializer(serializers.ModelSerializer):
    projectname = ProjnameSerializer(many=True, read_only=True)

    class Meta:
        model = PlatformName
        fields = ('id', 'platform_name', 'platform_memo', 'projectname')


class ProjectConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectConfig
        fields = '__all__'

class ProjTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_Config_Ticket
        fields = '__all__'

class DeployTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project_Deploy_Ticket
        fields = '__all__'


class Config_confd(object):
    pass


class ConfigConfdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config_Confd
        fields = '__all__'

class ConfdDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Confd_Detail
        fields = '__all__'

class AssetProviderSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(many=True, read_only=True)

    class Meta:
        model = AssetProvider
        fields = (
            'id', 'asset_provider_name', 'asset_provider_contact', 'asset_provider_telephone', 'asset_provider_memo',
            'assets')


class CabinetSerializer(serializers.ModelSerializer):
    assets = AssetsSerializer(many=True, read_only=True)

    class Meta:
        model = Cabinet
        fields = ('id', 'idc', 'cabinet_name', 'cabinet_memo', 'assets')


class IDCSerializer(serializers.ModelSerializer):
    cabinet = CabinetSerializer(many=True, read_only=True)
    assets = AssetsSerializer(many=True, read_only=True)

    class Meta:
        model = IDC
        fields = ('id', 'idc_name', 'idc_address', 'idc_contact', 'idc_telephone', 'idc_memo', 'cabinet', 'assets')


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AnsibleInventory
        fields = '__all__'


class FortSerializer(serializers.ModelSerializer):
    class Meta:
        model = FortServer
        fields = '__all__'


class FortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FortServerUser
        fields = '__all__'


class PeriodicTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = '__all__'


class WebSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebSite
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
