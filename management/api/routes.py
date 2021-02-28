from rest_framework import routers

from management.api.v1.viewsets import CompanyViewSet, OrderStateViewSet, \
    PaymentDetailAdmViewSet, PaymentMethodAdmViewSet, \
    ProductViewSet, ProductCategoryViewSet, ProductAttributeTypeViewSet, ProductAttributeTypeInstanceViewSet, \
    ProductSubItemViewSet, ProductImageViewSet, ProductImageViewSetForProduct, OrderViewSet
from shop.api.v1.viewsets import GuestViewSet, AddressViewSet, ContactViewSet, DeliveryViewSet, \
    ApplyVoucherViewSet, OrderItemViewSet, FileOrderItemViewSet, SelectOrderItemViewSet, NumberOrderItemViewSet, \
    CheckboxOrderItemViewSet, OrderDetailViewSet

router = routers.DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'orderstate', OrderStateViewSet)
router.register(r'orderdetails', OrderDetailViewSet)
router.register(r'paymentdetail', PaymentDetailAdmViewSet)
router.register(r'paymentmethod', PaymentMethodAdmViewSet)
router.register(r'products', ProductViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'productattributetypes', ProductAttributeTypeViewSet)
router.register(r'productattributetypeinstances', ProductAttributeTypeInstanceViewSet)
router.register(r'productsubitem', ProductSubItemViewSet)
router.register(r'accounts', GuestViewSet)
router.register(r'contacts/(?P<id>[0-9]*)/addresses', AddressViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'deliveries', DeliveryViewSet)
router.register(r'order', OrderViewSet)
router.register(r'voucher', ApplyVoucherViewSet)
router.register(r'orderitem', OrderItemViewSet)
router.register(r'fileorderitem', FileOrderItemViewSet)
router.register(r'selectorderitem', SelectOrderItemViewSet)
router.register(r'numberorderitem', NumberOrderItemViewSet)
router.register(r'checkboxorderitem', CheckboxOrderItemViewSet)
router.register(r'productimage', ProductImageViewSet)
router.register(r'product/(?P<id>[0-9]*)/productimage', ProductImageViewSetForProduct)
