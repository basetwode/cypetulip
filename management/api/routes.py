from rest_framework import routers

from management.api.v1.viewsets import CacheSettingViewSet, MailSettingViewSet, LdapSettingViewSet, ShopSettingViewSet, \
    LegalSettingViewSet, FooterViewSet, HeaderViewSet

router = routers.DefaultRouter()
router.register(r'settings/mail', MailSettingViewSet)
router.register(r'settings/ldap', LdapSettingViewSet)
router.register(r'settings/shop', ShopSettingViewSet)
router.register(r'settings/legal', LegalSettingViewSet)
router.register(r'settings/cache', CacheSettingViewSet)
router.register(r'headers', HeaderViewSet)
router.register(r'footers', FooterViewSet)
