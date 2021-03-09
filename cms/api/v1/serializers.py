from rest_framework import serializers

from cms.models.models import Page, Section


class PageSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Page
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Section
        fields = '__all__'
