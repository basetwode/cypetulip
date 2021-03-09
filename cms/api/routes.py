from rest_framework import routers

from cms.api.v1.viewsets import PageViewSet, SectionViewSet

router = routers.DefaultRouter()
router.register(r'pages', PageViewSet)
router.register(r'sections', SectionViewSet)
