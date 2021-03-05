from django.contrib import admin

# Register your models here.
from shop.models.accounts import Address, Company, Employee, Contact
from shop.models.orders import OrderItemState, OrderState, Discount, FixedAmountDiscount, PercentageDiscount, Order, \
    OrderDetail, OrderItem, FileOrderItem, SelectOrderItem, CheckBoxOrderItem, NumberOrderItem
from shop.models.products import ProductCategory, ProductSubItem, FileSubItem, FileExtensionItem, SelectSubItem, \
    SelectItem, NumberSubItem, CheckBoxSubItem, ProductAttributeType, ProductAttributeTypeInstance, Product, \
    ProductImage, IndividualOffer

admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Company)
admin.site.register(Contact)
admin.site.register(Employee)
admin.site.register(Discount)
admin.site.register(OrderDetail)
admin.site.register(OrderItem)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductCategory)
admin.site.register(SelectItem)
admin.site.register(CheckBoxOrderItem)
admin.site.register(CheckBoxSubItem)
admin.site.register(FileOrderItem)
admin.site.register(FileSubItem)
admin.site.register(FileExtensionItem)
admin.site.register(SelectOrderItem)
admin.site.register(SelectSubItem)
admin.site.register(NumberOrderItem)
admin.site.register(NumberSubItem)
admin.site.register(OrderState)
admin.site.register(OrderItemState)
admin.site.register(ProductAttributeType)
admin.site.register(ProductAttributeTypeInstance)
admin.site.register(IndividualOffer)
admin.site.register(ProductSubItem)
admin.site.register(FixedAmountDiscount)
admin.site.register(PercentageDiscount)