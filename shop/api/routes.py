from rest_framework import routers

from shop.api.v1.viewsets import CompanyViewSet, OrderStateViewSet, \
    ProductViewSet, ProductCategoryViewSet, ProductAttributeTypeViewSet, ProductAttributeTypeInstanceViewSet, \
    ProductSubItemViewSet, ProductImageViewSet, ProductImageViewSetForProduct, FileExtensionItemViewSet, \
    SelectItemViewSet, OrderItemStateViewSet, FixedAmountDiscountViewSet, PercentageDiscountViewSet, \
    WorkingTimeSerializerViewSet
from shop.api.v1.viewsets import GuestViewSet, AddressViewSet, ContactViewSet, DeliveryViewSet, \
    ApplyVoucherViewSet, OrderItemViewSet, FileOrderItemViewSet, SelectOrderItemViewSet, NumberOrderItemViewSet, \
    CheckboxOrderItemViewSet, OrderDetailViewSet

router = routers.DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'orderstate', OrderStateViewSet)
router.register(r'orderdetails', OrderDetailViewSet)
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
router.register(r'voucher', ApplyVoucherViewSet)
router.register(r'orderitem', OrderItemViewSet)
router.register(r'fileorderitem', FileOrderItemViewSet)
router.register(r'selectorderitem', SelectOrderItemViewSet)
router.register(r'numberorderitem', NumberOrderItemViewSet)
router.register(r'checkboxorderitem', CheckboxOrderItemViewSet)
router.register(r'productimage', ProductImageViewSet)
router.register(r'product/(?P<id>[0-9]*)/productimage', ProductImageViewSetForProduct)
router.register(r'fileextension', FileExtensionItemViewSet)
router.register(r'selectitem', SelectItemViewSet)
router.register(r'orderitemstate', OrderItemStateViewSet)
router.register(r'discounts/fixed', FixedAmountDiscountViewSet)
router.register(r'discounts/percentage', PercentageDiscountViewSet)
router.register(r'working-time', WorkingTimeSerializerViewSet)
