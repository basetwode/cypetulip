import django_filters
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from management.api.v1.serializers import MailSettingSerializer, LdapSettingSerializer, ShopSettingSerializer, \
    LegalSettingSerializer, HeaderSerializer, FooterSerializer, CacheSettingSerializer
from management.models.main import MailSetting, LdapSetting, ShopSetting, LegalSetting, Header, Footer, CacheSetting


class MailSettingViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = MailSetting.objects.all()
    serializer_class = MailSettingSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class LdapSettingViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = LdapSetting.objects.all()
    serializer_class = LdapSettingSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class ShopSettingViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = ShopSetting.objects.all()
    serializer_class = ShopSettingSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class LegalSettingViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = LegalSetting.objects.all()
    serializer_class = LegalSettingSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class HeaderViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Header.objects.all()
    serializer_class = HeaderSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class FooterViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Footer.objects.all()
    serializer_class = FooterSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class CacheSettingViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = CacheSetting.objects.all()
    serializer_class = CacheSettingSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
