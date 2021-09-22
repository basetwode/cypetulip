import math
import uuid
from datetime import datetime

from _decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

from billing.utils import calculate_sum_order, calculate_sum
from mediaserver.upload import invoice_files_upload_handler, fs, order_files_upload_handler
from shop.models.accounts import Company, Contact, Address
from shop.models.products import Product, ProductCategory, IndividualOffer, ProductSubItem, SelectItem


class OrderItemState(models.Model):
    name = models.CharField(max_length=20)
    next_state = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='previous_state',
        verbose_name=_('Next state'))

    class Meta:
        verbose_name = _("OrderItemState")
        verbose_name_plural = _("OrderItemStates")


class OrderState(models.Model):
    name = models.CharField(max_length=20)
    initial = models.BooleanField(default=False)
    cancel_order_state = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='cancel_state', )
    next_state = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='previous_state', )
    is_paid_state = models.BooleanField(default=False)
    is_sent_state = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Order State')
        verbose_name_plural = _('Order States')

    # todo states have corresponding actions that also need to be linked!

    def __str__(self):
        return self.name

    def last_state(self):
        if self is not None:
            if self == self.next_state and self.next_state != self.cancel_order_state:
                return True
            else:
                return False
        else:
            return False


class Discount(models.Model):
    voucher_id = models.CharField(unique=True, max_length=20, default="VOUCHER")
    eligible_products = models.ManyToManyField(Product, blank=True, verbose_name=_('Eligible products'))
    eligible_categories = models.ManyToManyField(ProductCategory, blank=True,
                                                 verbose_name=_('Eligible categories'))
    valid_until_date = models.DateTimeField(blank=True, null=True)
    count = models.IntegerField(default=0)
    valid_until_count = models.IntegerField(default=-1)
    enabled = models.BooleanField(default=True)
    show_in_products = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True, blank=True)

    def is_invalid(self):
        is_expired = datetime.now() > self.valid_until_date if self.valid_until_date else False
        is_utilized = self.count >= self.valid_until_count if self.valid_until_count > 0 else False
        return is_expired or is_utilized or not self.enabled

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Discount, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        verbose_name = _('Discount')
        verbose_name_plural = _('Discounts')

    def __str__(self):
        return self.voucher_id


class FixedAmountDiscount(Discount):
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.voucher_id

    class Meta:
        verbose_name = _("FixedAmountDiscount")
        verbose_name_plural = _("FixedAmountDiscounts")


class PercentageDiscount(Discount):
    discount_percentage = models.FloatField(default=0)

    def __str__(self):
        return self.voucher_id

    class Meta:
        verbose_name = _("PercentageDiscount")
        verbose_name_plural = _("PercentageDiscounts")

    def discount_percentage_in_percent(self):
        return int(self.discount_percentage * 100)


class OrderDetail(models.Model):
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, null=True, blank=True)
    is_send = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Company'))
    session = models.CharField(max_length=40, blank=True, null=True)
    individual_offer_request = models.ForeignKey(IndividualOffer, on_delete=models.SET_NULL, blank=True, null=True,
                                                 editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    assigned_employee = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Assigned employee'),
        related_name='employee')
    state = models.ForeignKey(OrderState, on_delete=models.CASCADE, null=True,
                              blank=True, verbose_name=_('State'))
    date_bill = models.DateTimeField(null=True, blank=True)
    bill_sent = models.BooleanField(default=False, blank=True)
    bill_file = models.FileField(default=None, null=True,
                                 upload_to=invoice_files_upload_handler,
                                 storage=fs)
    bill_number = models.IntegerField(default=None, blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Contact'))
    shipment_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='shipment_address', verbose_name=_('Shipment address'))
    billing_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='billing_address', verbose_name=_('Billing address'))
    is_cancelled = models.BooleanField(default=False, blank=True, null=True, editable=False)
    discount = models.ForeignKey(Discount, default=None, blank=True, null=True, on_delete=models.SET_NULL,
                                 verbose_name=_('Discount'))
    discount_code = models.CharField(default="", max_length=20, blank=True, null=True, editable=False)
    discount_amount = models.FloatField(default=0, blank=True, null=True, editable=False)
    discount_percentage = models.FloatField(default=0, blank=True, null=True, editable=False)

    def __str__(self):
        return self.uuid.__str__()

    class Meta:
        verbose_name = _("OrderDetail")
        verbose_name_plural = _("OrderDetails")

    @staticmethod
    def create_new_order(request):
        if request.user.is_authenticated:
            company = request.user.contact.company
            order_detail = OrderDetail(company=company,
                                       contact=request.user.contact)
            order_detail.save()
            return order_detail
        else:
            order_detail = OrderDetail(session=request.session.session_key)
            order_detail.save()
            return order_detail

    def unique_nr(self):
        return "CT-NR" + str(self.id).rjust(10, "0")

    def unique_bill_nr(self):
        return "CT-INR" + str(self.bill_number).rjust(10, "0")

    def send_order(self):
        self.date_added = datetime.now()
        self.save()

    def apply_voucher(self, voucher):
        if self.discount:
            return False
        voucher_applied = [order_item.apply_discount_if_eligible(voucher) for order_item in self.orderitem_set.all()]
        if True not in voucher_applied:
            return False
        self.discount = voucher
        self.discount_code = voucher.voucher_id
        if hasattr(voucher, 'percentagediscount'):
            self.discount_percentage = voucher.percentagediscount.discount_percentage
            self.save()
            self.apply_discount()
        elif hasattr(voucher, 'fixedamountdiscount'):
            self.discount_amount = voucher.fixedamountdiscount.amount
            self.orderitem_set.order_by('-price').first() \
                .apply_discount_if_eligible(voucher, apply_fixed_discount=True)
            self.save()
        voucher.count += 1
        voucher.save()
        return True

    def remove_voucher(self):
        if self.discount:
            self.discount_amount = 0
            self.discount_percentage = 0
            self.discount_code = ""
            self.discount.count -= 1
            self.discount.save()
            self.discount = None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        if self.__was_canceled():
            self.increase_stocks()
            self.is_cancelled = True
        elif self.__was_uncancelled():
            self.decrease_stocks()
            self.is_cancelled = False
        if not self.state and self.orderitem_set.count() == 0:
            self.remove_voucher()
        if not self.company and self.contact:
            self.company = self.contact.company
            self.save()
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def delete(self, using=None, keep_parents=False):
        self.increase_stocks()
        super(OrderDetail, self).delete(using, keep_parents)

    def increase_stocks(self):
        for order_item in self.orderitem_set.all():
            if hasattr(order_item.product, 'product') and isinstance(order_item.product.product, Product):
                order_item.product.product.increase_stock(order_item.count)

    def decrease_stocks(self):
        for order_item in self.orderitem_set.all():
            if hasattr(order_item.product, 'product') and isinstance(order_item.product.product, Product):
                order_item.product.product.decrease_stock(order_item.count)

    def apply_discount(self):
        for order_item in self.orderitem_set.all():
            order_item.save()

    def remove_discount(self):
        for order_item in self.orderitem_set.all():
            order_item.save()

    def __was_canceled(self):
        return self.state == OrderState.objects.get(initial=True).cancel_order_state and \
               not self.is_cancelled

    def __was_uncancelled(self):
        return self.state != OrderState.objects.get(initial=True).cancel_order_state and \
               self.is_cancelled

    @extend_schema_field(OpenApiTypes.DOUBLE)
    def total_wt(self, include_discount=False):
        return Decimal(f"{calculate_sum_order(self.orderitem_set, True, include_discount) or 0}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @extend_schema_field(OpenApiTypes.DOUBLE)
    def total(self, include_discount=False):
        return Decimal(f"{calculate_sum_order(self.orderitem_set, False, include_discount) or 0}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def total_discounted(self):
        return self.total(True)  # - (self.discount_amount or 0)

    def total_discounted_wt(self):
        return self.total_wt(True)  # - (self.discount_amount or 0)

    def tax(self):
        return self.total_discounted_wt() - self.total_discounted()

    def total_discount(self):
        return round(self.total() - self.total_discounted(), 2)

    def total_discount_wt(self):
        return round(self.total_wt() - self.total_discounted_wt(), 2)

    def discount_str(self):
        return f"{int(self.discount_percentage * 100)} %" if self.discount_percentage else f"{self.discount_amount} €"


class OrderItem(models.Model):
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, default=None, blank=True, null=True)
    product = models.ForeignKey(ProductSubItem, null=True, blank=True, on_delete=models.CASCADE)
    order_item = models.ForeignKey(
        'OrderItem', on_delete=models.CASCADE, null=True, blank=True, )
    employee = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True, )
    additional_text = models.CharField(max_length=200, null=True, blank=True)
    state = models.ForeignKey(
        OrderItemState, on_delete=models.CASCADE, null=True, blank=True, )
    count = models.IntegerField(default=1)
    tax_rate = models.IntegerField(default=None, blank=True, null=True)
    price = models.FloatField(default=None, blank=True, null=True)
    price_wt = models.FloatField(default=None, blank=True, null=True)
    price_discounted = models.FloatField(default=None, blank=True, null=True)
    price_discounted_wt = models.FloatField(default=None, blank=True, null=True)
    applied_discount = models.FloatField(default=None, blank=True, null=True)
    period_of_performance_start = models.DateTimeField(null=True, blank=True)
    period_of_performance_end = models.DateTimeField(null=True, blank=True)
    allowable = models.BooleanField(default=True, blank=True, null=True)

    class Meta:
        verbose_name = _("OrderItem")
        verbose_name_plural = _("OrderItems")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, recalculate_tax=False):
        price_changed = self.price_changed()

        if (
                not self.order_detail.state or not self.price) and price_changed and self.product and not self.product.price_on_request:
            self.price = self.get_product_special_price() if self.get_product_special_price() else self.get_product_price()
            self.price_wt = self.get_product_price_wt()
            self.applied_discount = 0
            self.price_discounted = self.get_product_price_b()
            self.price_discounted_wt = self.get_product_price_wt()
        if self.product.price_on_request and not self.price_wt:
            self.price_wt = self.calculate_tax(self.price)
            self.applied_discount = 0
            self.price_discounted = self.price
            self.price_discounted_wt = self.price_wt
        if not self.pk or price_changed:
            self.apply_discount_if_eligible(self.order_detail.discount,
                                            save=False) if self.order_detail.discount else None
        if not math.isclose(self.price_wt, self.calculate_tax(self.price), rel_tol=1e-5):
            self.price_wt = self.calculate_tax(self.price)
            self.applied_discount = 0
            self.price_discounted = self.price
            self.price_discounted_wt = self.price_wt
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)
        for order_item in OrderItem.objects.filter(order_item=self):
            order_item.save()
        if not self.tax_rate:
            self.tax_rate = int(self.product.tax * 100)
            self.save()

    def delete(self, using=None, keep_parents=False):
        if hasattr(self.product, 'product'):
            self.product.product.increase_stock()
        super(OrderItem, self).delete(using, keep_parents)
        self.order_detail.save()

    def is_discount_eligible(self, voucher):

        product_id_in_discount = voucher.eligible_products.filter(id=self.product.id).exists()
        parent_product_in_discount = self.product.product.assigned_sub_products.filter(id=self.product.id).exists() if \
            hasattr(self.product, 'product') else False
        product_category_in_discount = voucher.eligible_categories.filter(
            id=self.product.product.category.id).exists() \
            if hasattr(self.product, 'product') else False
        is_parent_item_eligible = self.order_item.is_discount_eligible(voucher) if self.order_item else False
        return product_id_in_discount or parent_product_in_discount or product_category_in_discount or is_parent_item_eligible

    def apply_discount_if_eligible(self, voucher, apply_fixed_discount=False, save=True):
        is_eligible = self.is_discount_eligible(voucher)
        result = False
        if is_eligible and hasattr(voucher, 'percentagediscount'):
            self.applied_discount = round(self.price * voucher.percentagediscount.discount_percentage, 2)
            self.price_discounted = round(self.price - self.applied_discount, 2)
            self.price_discounted_wt = self.calculate_tax(self.price_discounted)
            result = True
        elif apply_fixed_discount:
            amount = voucher.fixedamountdiscount.amount if voucher.fixedamountdiscount.amount < self.price else self.price
            self.price_discounted_wt = round(self.price_wt - amount, 2)
            self.price_discounted = round(self.price_discounted_wt / (1 + self.product.tax), 2)
            self.applied_discount = self.price_discounted_wt - self.price_discounted
            result = True
        else:
            self.applied_discount = 0
            self.price_discounted = self.get_product_price_b()
            self.price_discounted_wt = self.price_wt
        # Fixed amount vouchers apply on the order not an individual item
        if is_eligible:
            result = True
        if save:
            self.save()
        return result

    def __str__(self):
        return f"{self.count}x {self.product.name if self.product else ''} {self.price}"

    @extend_schema_field(OpenApiTypes.DOUBLE)
    def total_wt(self, include_discount=False):
        if not self.allowable:
            return 0
        sub_items = OrderItem.objects.filter(order_item=self)
        sum = (calculate_sum(sub_items, True, include_discount) + (
            (float(self.price_wt) if not include_discount else self.price_discounted_wt) \
                if sub_items.count() > 0 else 0 + float(
                self.price_wt) if not include_discount else self.price_discounted_wt)) * \
              self.count
        return Decimal(f"{sum}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def total(self, include_discount=False):
        if not self.allowable:
            return 0
        sub_items = OrderItem.objects.filter(order_item=self)
        return (calculate_sum(sub_items, False, include_discount) + (
            self.price if not include_discount else self.price_discounted) \
                    if sub_items.count() > 0 else 0 + self.price if not include_discount else self.price_discounted) * \
               self.count

    def total_discounted(self):
        return round(self.total(True), 2)

    def total_discounted_wt(self):
        return round(self.total_wt(True), 2)

    def total_discount(self):
        return round(self.total() - self.total_discounted(), 2)

    def total_discount_wt(self):
        return round(self.total_wt() - self.total_discounted_wt(), 2)

    def calculate_tax(self, price):
        return Decimal(f"{price * (1 + self.product.tax)}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def get_product_price(self):
        return self.product.price if hasattr(self, 'fileorderitem') else \
            self.checkboxorderitem.get_product_price() if hasattr(self, 'checkboxorderitem') else \
                self.selectorderitem.get_product_price() if hasattr(self, 'selectorderitem') else \
                    self.product.price

    def get_product_special_price(self):
        return self.product.special_price if hasattr(self, 'fileorderitem') else \
            self.checkboxorderitem.get_product_special_price() if hasattr(self, 'checkboxorderitem') else \
                self.selectorderitem.get_product_special_price() if hasattr(self, 'selectorderitem') else \
                    self.product.special_price

    def get_product_price_wt(self):
        return (self.calculate_tax(self.get_product_special_price()) if self.get_product_special_price() else
                self.calculate_tax(self.get_product_price()))

    def get_product_price_b(self):
        return (self.get_product_special_price() if self.get_product_special_price() else
                self.get_product_price())

    def price_changed(self):
        return \
            (not self.price_wt or self.price_wt != self.calculate_tax(self.price)) if hasattr(self,
                                                                                              'fileorderitem') else \
                self.checkboxorderitem.price_changed() if hasattr(self, 'checkboxorderitem') else \
                    self.selectorderitem.price_changed() if hasattr(self, 'selectorderitem') else \
                        (not self.price_wt or self.price_wt != self.calculate_tax(self.price))

    def is_conveyed(self):
        return self.shipment_set.exists()

class FileOrderItem(OrderItem):
    file = models.FileField(default=None, null=True,
                            upload_to=order_files_upload_handler,
                            storage=fs)
    file_name = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = _("FileOrderItem")
        verbose_name_plural = _("FileOrderItems")


class SelectOrderItem(OrderItem):
    selected_item = models.ForeignKey(SelectItem, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("SelectOrderItem")
        verbose_name_plural = _("SelectOrderItems")

    def get_product_price(self):
        return self.selected_item.price if self.selected_item else 0

    def get_product_special_price(self):
        return self.selected_item.price if self.selected_item else 0

    def price_changed(self):
        return self.price_wt != self.selected_item.price_wt()


class CheckBoxOrderItem(OrderItem):
    is_checked = models.BooleanField()

    class Meta:
        verbose_name = _("CheckBoxOrderItem")
        verbose_name_plural = _("CheckBoxOrderItems")

    def get_product_price(self):
        return self.product.price if self.is_checked else 0

    def get_product_special_price(self):
        return self.product.special_price if self.is_checked else 0

    def price_changed(self):
        return (not self.price_wt and self.is_checked) or (
                not not self.price_wt and not self.is_checked) or not self.price_wt


class NumberOrderItem(OrderItem):
    number = models.IntegerField()

    class Meta:
        verbose_name = _("NumberOrderItem")
        verbose_name_plural = _("NumberOrderItems")


@receiver(pre_delete, sender=FileOrderItem)
def fileorderitem_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
