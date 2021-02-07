from rest_framework import routers

from accounting.api.v1.viewsets import AccountingOrderDetailPerYearViewSet
from management.api.v1.viewsets import CompanyViewSet, ContactAdmViewSet, AddressAdmViewSet, OrderStateViewSet, \
    OrderAdmViewSet, OrderDetailAdmViewSet, OrderItemAdmViewSet, FileOrderItemAdmViewSet, CheckboxOrderItemAdmViewSet, \
    SelectOrderItemAdmViewSet, NumberOrderItemAdmViewSet, PaymentDetailAdmViewSet, PaymentMethodAdmViewSet, \
    ProductViewSet, ProductCategoryViewSet, ProductAttributeTypeViewSet, ProductAttributeTypeInstanceViewSet, \
    ProductSubItemViewSet, ProductImageViewSet, ProductImageViewSetForProduct
from shop.api.viewsets.rest import GuestViewSet, AddressViewSet, ContactViewSet, DeliveryViewSet, OrderViewSet, \
    ApplyVoucherViewSet, OrderItemViewSet, FileOrderItemViewSet, SelectOrderItemViewSet, NumberOrderItemViewSet, \
    CheckboxOrderItemViewSet

router = routers.DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'adm/contacts', ContactAdmViewSet)
router.register(r'adm/contacts/(?P<id>[0-9]*)/addresses', AddressAdmViewSet)
router.register(r'adm/orderstate', OrderStateViewSet)
router.register(r'adm/order', OrderAdmViewSet)
router.register(r'adm/orderdetails/(?P<order_hash>[a-zA-Z0-9\\s\-_ ]*)', OrderDetailAdmViewSet)
router.register(r'adm/orderdetails', OrderDetailAdmViewSet)
router.register(r'adm/orderitem', OrderItemAdmViewSet)
router.register(r'adm/fileorderitem', FileOrderItemAdmViewSet)
router.register(r'adm/checkboxorderitem', CheckboxOrderItemAdmViewSet)
router.register(r'adm/selectorderitem', SelectOrderItemAdmViewSet)
router.register(r'adm/numberorderitem', NumberOrderItemAdmViewSet)
router.register(r'adm/paymentdetail', PaymentDetailAdmViewSet)
router.register(r'adm/paymentmethod', PaymentMethodAdmViewSet)
router.register(r'products', ProductViewSet)
router.register(r'categories', ProductCategoryViewSet)
router.register(r'productattributetypes', ProductAttributeTypeViewSet)
router.register(r'productattributetypeinstances', ProductAttributeTypeInstanceViewSet)
router.register(r'productsubitem', ProductSubItemViewSet)
router.register(r'accounts', GuestViewSet)
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
router.register(r'product/(?P<productId>[0-9]*)/productimage', ProductImageViewSetForProduct)
router.register(r'accounting/orders/(?P<year>[0-9]{4})', AccountingOrderDetailPerYearViewSet)
