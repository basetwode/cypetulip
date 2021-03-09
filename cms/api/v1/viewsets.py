import django_filters
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser

from cms.api.v1.serializers import PageSerializer, SectionSerializer
from cms.models.models import Page, Section


class PageViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


class SectionViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsAdminUser]
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
