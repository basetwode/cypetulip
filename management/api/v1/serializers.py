from rest_framework import serializers

from management.models.models import MailSetting, LdapSetting, ShopSetting, LegalSetting, Header, CacheSetting, Footer


class MailSettingSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = MailSetting
        fields = '__all__'


class LdapSettingSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = LdapSetting
        fields = '__all__'


class ShopSettingSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = ShopSetting
        fields = '__all__'


class LegalSettingSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = LegalSetting
        fields = '__all__'


class HeaderSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Header
        fields = '__all__'


class FooterSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Footer
        fields = '__all__'


class CacheSettingSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = CacheSetting
        fields = '__all__'
