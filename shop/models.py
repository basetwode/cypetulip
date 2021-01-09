from datetime import datetime

from _decimal import ROUND_HALF_UP, Decimal
from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.db.models import Sum, Q
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _
from tinymce import HTMLField

from billing.utils import calculate_sum, calculate_sum_order
from mediaserver.upload import (company_files_upload_handler, fs, order_files_upload_handler,
                                public_files_upload_handler, rand_key, invoice_files_upload_handler)


class Company(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    company_id = models.CharField(max_length=100, blank=True, null=True)
    customer_nr = models.IntegerField(blank=True, null=True, verbose_name=_('Customer Nr'))
    term_of_payment = models.IntegerField(default=10, verbose_name=_('Term of payment'))
    street = models.CharField(max_length=40, default=None, verbose_name=_('Street'))
    number = models.CharField(max_length=5, default=None, verbose_name=_('Number'))
    zipcode = models.CharField(max_length=5, default=None, verbose_name=_('Zipcode'))
    city = models.CharField(max_length=30, default=None, verbose_name=_('City'))
    logo = models.FileField(default=None, null=True, blank=True,
                            upload_to=company_files_upload_handler, storage=fs)

    class Meta:
        verbose_name_plural = "Companies"
        verbose_name = "Company"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.company_id is None or len(self.company_id) == 0:
            self.company_id = rand_key(12)
        if self.customer_nr is None:
            nr = (Company.objects.all().order_by('customer_nr').last().customer_nr + 1) \
                if Company.objects.all().count() > 0 and Company.objects.filter(customer_nr__isnull=False).exists() else 1
            self.customer_nr = nr
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def __str__(self):
        return self.name or ""


class Contact(DjangoUser):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('D', _('Others')),
    )
    session = models.CharField(max_length=40, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name=_('Company'))
    company_customer_nr = models.IntegerField(blank=True, null=True, verbose_name=_('Company Customer Nr'))
    title = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Title'))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name=_('Gender'))
    telephone = models.CharField(max_length=40, verbose_name=_('Telephone'))
    language = models.CharField(max_length=2, default='en', verbose_name=_('Language'))

    def __str__(self):
        return str(self.company) + ' - ' + self.last_name + ' ' + self.first_name + f" ({self.username})"

    def is_registered(self):
        return self.groups.filter(name="client").exists()

    def customer_nr(self):
        return "C" + str(self.company.customer_nr).rjust(7, "0") + str(self.company_customer_nr).rjust(3, "0")

    class Meta:
        verbose_name = _('Contact')

    def save(self, force_insert=False, force_update=False, using=None,
         update_fields=None):

        if self.company_customer_nr is None:
            nr = (Contact.objects.filter(company=self.company, company_customer_nr__isnull=False).order_by(
                'company_customer_nr').last().company_customer_nr + 1) \
                if Contact.objects.filter(company=self.company, company_customer_nr__isnull=False).exists() else 1
            self.company_customer_nr = nr
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

class Address(models.Model):
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=40, default=None, verbose_name=_('Street'))
    number = models.CharField(max_length=5, default=None, verbose_name=_('Number'))
    zipcode = models.CharField(max_length=5, default=None, verbose_name=_('Zipcode'))
    city = models.CharField(max_length=100, default=None, verbose_name=_('City'))
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, default=None, blank=True, null=True,
                                verbose_name=_('Contact'))

    class Meta:
        verbose_name_plural = "Addresses"
        verbose_name = _('Address')

    def __str__(self):
        return self.contact.__str__() + " | " + self.name


class ProductCategory(models.Model):
    path = models.CharField(max_length=300, verbose_name=_('Path'), null=True, blank=True)
    description = models.CharField(max_length=300, verbose_name=_('Description'))
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    mother_category = models.ForeignKey(
        'self', on_delete=models.CASCADE, default=None, blank=True, null=True, verbose_name=_('Parent Category'))
    child_categories = models.ManyToManyField('self', default=None, blank=True, symmetrical=False,
                                              related_name='ChildCategories', verbose_name=_('Child Category'))
    is_main_category = models.BooleanField(default=False, verbose_name=_('Is main category'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')

    def build_path(self, path=""):
        return self.mother_category.build_path(self.name+("-"+path if path else "")) if self.mother_category else self.name+("-"+path if path else "")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.path = self.build_path()
        super(ProductCategory, self).save(force_insert, force_update, using, update_fields)


class Employee(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, default=None)
    first_name = models.CharField(max_length=100, verbose_name=_('Firstname'))
    last_name = models.CharField(max_length=100, verbose_name=_('Lastname'))

    class Meta:
        verbose_name = _('Employee')


# This is an orderable item which shows up when ordering a product that is public.
# like squaremeter notes on a plan


class ProductSubItem(models.Model):
    price = models.FloatField(verbose_name=_('Price'))
    special_price = models.FloatField(default=False, blank=True, null=True, verbose_name=_('Special price'))
    price_on_request = models.BooleanField(default=False, blank=True, null=True, verbose_name=_('Price on request'))
    tax = models.FloatField(default=0.19, blank=False, null=False, verbose_name=_('Tax'))
    name = models.CharField(max_length=30)
    description = HTMLField(_('Description'))
    details = HTMLField(_('Details'))
    requires_file_upload = models.BooleanField(default=False, verbose_name=_('Requires file upload'))
    is_required = models.BooleanField(default=False, verbose_name=_('Is required'))
    is_multiple_per_item = models.BooleanField(default=False, verbose_name=_('Is multiple per item'))
    is_once_per_order = models.BooleanField(default=False, verbose_name=_('Is once per order'))

    def __str__(self):
        if hasattr(self, 'product'):
            return f"{self.product.category} | {self.name} ({self.product.get_stock()}) | {self.price} €"
        else:
            return f"{self.name} | {self.price}"

    def calculate_tax(self, price):
        return Decimal(f"{price * (1 + self.tax)}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def price_wt(self):
        return self.calculate_tax(self.price)

    def special_price_wt(self):
        return self.calculate_tax(self.special_price) if self.special_price else None

    def bprice_wt(self):
        return self.special_price_wt() if self.special_price else self.price_wt()


class FileSubItem(ProductSubItem):
    # name = models.CharField(max_length=20)
    extensions = models.CharField(max_length=200, null=True, blank=True, default="")
    file = models.FileField(default=None, null=True, blank=True,
                            upload_to=order_files_upload_handler, storage=fs)


class FileExtensionItem(models.Model):
    extension = models.CharField(max_length=30)
    file = models.ForeignKey(FileSubItem, on_delete=models.CASCADE)


# can be used for sizes for example
class SelectSubItem(ProductSubItem):
    pass
    # name = models.CharField(max_length=20)


# different options for sizes for example
class SelectItem(models.Model):
    name = models.CharField(max_length=40)
    select = models.ForeignKey(SelectSubItem, on_delete=models.CASCADE)
    price = models.FloatField(verbose_name=_('Price'),default=0)
    tax = models.FloatField(default=0.19, blank=False, null=False, verbose_name=_('Tax'))

    def __str__(self):
        return self.name

    def price_wt(self):
        return Decimal(f"{self.price * (1 + self.tax)}")\
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# can be used for number of this item like 4 trousers
class NumberSubItem(ProductSubItem):
    pass
    # name = models.CharField(max_length=20)


# can be used for "as a present" or "moebliert" for example
class CheckBoxSubItem(ProductSubItem):
    pass


'''
    State of a single order item eg. sent, going to be send, delivered
'''


class OrderItemState(models.Model):
    name = models.CharField(max_length=20)
    next_state = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='previous_state',
        verbose_name=_('Next state'))


'''
    State of an order, eg. payment received, waiting for payment, ...
'''


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


class ProductAttributeType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProductAttributeTypeInstance(models.Model):
    type = models.ForeignKey(ProductAttributeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ['type']

    def __str__(self):
        return self.type.__str__() + " | " + self.value


# A product can be whatever one needs, like a plan or a surcharge or hours worked..

class Product(ProductSubItem):
    stock = models.IntegerField(default=0, blank=True, null=True, verbose_name=_('Stock'))
    max_items_per_order = models.IntegerField(default=10, verbose_name=_('Maximum number of items per order'))
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    is_public = models.BooleanField()
    assigned_sub_products = models.ManyToManyField(ProductSubItem, default=None, blank=True,
                                                   symmetrical=False,
                                                   related_name='sub_products', verbose_name=_('Assigned sub products'))
    attributes = models.ManyToManyField(ProductAttributeTypeInstance, blank=True, verbose_name=_('Attributes'))

    class Meta:
        verbose_name = _('Product')


    def decrease_stock(self, number_of_items=1):
        self.stock = self.stock - number_of_items if self.stock > 0 else self.stock
        self.save()

    def increase_stock(self, number_of_items=1):
        self.stock = self.stock + number_of_items if self.stock > -1 else self.stock
        self.save()

    def get_stock(self):
        return f"{self.stock if self.stock > -1 else '~'}"

    def is_stock_sufficient(self, order):
        order_items_count_with_product = order.orderitem_set.filter(product=self)\
            .aggregate(count=Sum('count'))['count'] or 0

        return self.stock == -1 or (self.stock > order_items_count_with_product), self.stock - order_items_count_with_product

    def product_picture(self):
        return self.productimage_set.first().product_picture if self.productimage_set.count() > 0 else None

    def get_also_bought_products(self):
        from django.db.models import Count
        related_orderitems = OrderItem.objects.filter(order_detail__in=OrderDetail.objects.filter(orderitem__product=self),
                                                      order_item__isnull=True).exclude(product=self).order_by('product')
        return Product.objects.all()\
            .annotate(ocount=Count('orderitem', filter=Q(orderitem__in=related_orderitems)))\
            .filter(ocount__gt=0)\
            .order_by('-ocount')

    def get_related_products(self):
        return Product.objects.filter(category=self.category)


class ProductImage(models.Model):
    order = models.IntegerField(default=0, blank=True)
    product_picture = models.ImageField(default=None, null=True, blank=True,
                                        upload_to=public_files_upload_handler,
                                        storage=fs, verbose_name=_('Product picture'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class IndividualOffer(models.Model):
    date_added = models.DateTimeField(auto_now=True, blank=True)
    mail = models.EmailField()
    message = models.CharField(max_length=1000)
    contact = models.ForeignKey(Contact, null=True, blank=True, default=None, editable=False, on_delete=models.CASCADE,
                                verbose_name=_('Contact'))
    product = models.ForeignKey(Product, editable=False, null=True, on_delete=models.SET_NULL,
                                verbose_name=_('Product'))

    def is_new(self):
        return (datetime.now().date() - self.date_added.date()).days < 3

    class Meta:
        verbose_name = _('Individual offer')


class Discount(models.Model):
    voucher_id = models.CharField(unique=True, max_length=20, default="VOUCHER")
    eligible_products = models.ManyToManyField(Product, blank=True, null=True, verbose_name=_('Eligible products'))
    eligible_categories = models.ManyToManyField(ProductCategory, blank=True, null=True,
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


class FixedAmountDiscount(Discount):
    amount = models.FloatField(default=0)


class PercentageDiscount(Discount):
    discount_percentage = models.FloatField(default=0)

    def discount_percentage_in_percent(self):
        return int(self.discount_percentage * 100)


class Order(models.Model):
    order_id = models.IntegerField(null=True, blank=True)
    order_hash = models.CharField(max_length=30, null=True, blank=True)
    is_send = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Company'))
    token = models.CharField(max_length=25, blank=True, null=True)
    session = models.CharField(max_length=40, blank=True, null=True)
    individual_offer_request = models.ForeignKey(IndividualOffer, on_delete=models.SET_NULL, blank=True, null=True,
                                                 editable=False)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.order_hash is None or len(self.order_hash) == 0:
            self.order_hash = rand_key(12)
        if self.order_id is None:
            orders = self.__class__.objects.all().order_by("-order_id")
            if orders:
                self.order_id = self.__class__.objects.all().order_by(
                    "-order_id")[0].order_id + 1
            else:
                self.order_id = 1
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.orderdetail_set.count() > 0:
            self.orderdetail_set.first().increase_stocks()
        super(Order, self).delete(using, keep_parents)

    def __str__(self):
        return str(self.order_id)

    @staticmethod
    def create_new_order(request):
        if request.user.is_authenticated:
            company = request.user.contact.company
            order = Order(is_send=False, company=company)
            order.save()
            order_detail = OrderDetail(order=order, order_number=order.order_hash,
                                       contact=request.user.contact)
            order_detail.save()
            return order, order_detail
        else:
            order = Order(is_send=False, session=request.session.session_key)
            order.save()
            order_detail = OrderDetail(order=order, order_number=order.order_hash)
            order_detail.save()
            return order, order_detail


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=30)
    date_added = models.DateTimeField(auto_now_add=True)
    assigned_employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('Assigned employee'))
    state = models.ForeignKey(OrderState, on_delete=models.CASCADE, null=True,
                              blank=True, verbose_name=_('State'))
    date_bill = models.DateTimeField(null=True, blank=True)
    bill_sent = models.BooleanField(default=False, blank=True)
    bill_file = models.FileField(default=None, null=True,
                            upload_to=invoice_files_upload_handler,
                            storage=fs)
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

    def unique_nr(self):
        return "CTNR" + str(self.id).rjust(10, "0")

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
        if self.__was_canceled():
            self.increase_stocks()
            self.is_cancelled = True
        elif self.__was_uncancelled():
            self.decrease_stocks()
            self.is_cancelled = False
        if not self.state and self.orderitem_set.count() == 0:
            self.remove_voucher()

        if not self.order.company and self.contact:
            self.order.company = self.contact.company
            self.order.save()
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def increase_stocks(self):
        for order_item in self.order.orderitem_set.all():
            if hasattr(order_item.product, 'product') and isinstance(order_item.product.product, Product):
                order_item.product.product.increase_stock(order_item.count)

    def decrease_stocks(self):
        for order_item in self.order.orderitem_set.all():
            if hasattr(order_item.product, 'product') and isinstance(order_item.product.product, Product):
                order_item.product.product.decrease_stock(order_item.count)

    def apply_discount(self):
        for order_item in self.order.orderitem_set.all():
            order_item.save()

    def remove_discount(self):
        for order_item in self.order.orderitem_set.all():
            order_item.save()

    def __was_canceled(self):
        return self.state == OrderState.objects.get(initial=True).cancel_order_state and \
               not self.is_cancelled

    def __was_uncancelled(self):
        return self.state != OrderState.objects.get(initial=True).cancel_order_state and \
               self.is_cancelled

    def total_wt(self, include_discount=False):
        return Decimal(f"{calculate_sum_order(self.orderitem_set, True, include_discount) or 0}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

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


# Like a surcharge or discount or product or whatever.


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_detail = models.ForeignKey(OrderDetail, on_delete=models.CASCADE, default=None, blank=True, null=True)
    product = models.ForeignKey(ProductSubItem, null=True, blank=True, on_delete=models.CASCADE)
    order_item = models.ForeignKey(
        'OrderItem', on_delete=models.CASCADE, null=True, blank=True, )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True, )
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, recalculate_tax=False):
        price_changed = self.price_changed()

        if (not self.order_detail.state or not self.price) and price_changed and self.product and not self.product.price_on_request:
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
        if self.price_wt != self.calculate_tax(self.price):
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

    def total_wt(self, include_discount=False):
        if not self.allowable:
            return 0
        sub_items = OrderItem.objects.filter(order_item=self)
        sum = (calculate_sum(sub_items, True, include_discount)  + (
            (float(self.price_wt) if not include_discount else self.price_discounted_wt) \
            if sub_items.count() > 0 else 0 + float(self.price_wt) if not include_discount else self.price_discounted_wt)) * \
               self.count
        return Decimal(f"{sum}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def total(self, include_discount=False):
        if not self.allowable:
            return 0
        sub_items = OrderItem.objects.filter(order_item=self)
        return (calculate_sum(sub_items, False, include_discount) + (
            self.price if not include_discount else self.price_discounted) \
            if sub_items.count() > 0 else 0 + self.price if not include_discount else self.price_discounted)  * \
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
            (not self.price_wt or self.price_wt != self.calculate_tax(self.price)) if hasattr(self, 'fileorderitem') else \
            self.checkboxorderitem.price_changed() if hasattr(self, 'checkboxorderitem') else \
                self.selectorderitem.price_changed() if hasattr(self, 'selectorderitem') else \
                    (not self.price_wt or self.price_wt != self.calculate_tax(self.price))


# Corresponding OrderItems for the subproducts
class FileOrderItem(OrderItem):
    file = models.FileField(default=None, null=True,
                            upload_to=order_files_upload_handler,
                            storage=fs)
    file_name = models.CharField(max_length=200, blank=True)


class SelectOrderItem(OrderItem):
    selected_item = models.ForeignKey(SelectItem, on_delete=models.CASCADE)

    def get_product_price(self):
        return self.selected_item.price if self.selected_item else 0

    def get_product_special_price(self):
        return self.selected_item.price if self.selected_item else 0

    def price_changed(self):
        return self.price_wt != self.selected_item.price_wt()


class CheckBoxOrderItem(OrderItem):
    is_checked = models.BooleanField()

    def get_product_price(self):
        return self.product.price if self.is_checked else 0

    def get_product_special_price(self):
        return self.product.special_price if self.is_checked else 0

    def price_changed(self):
        return (not self.price_wt and self.is_checked) or (not not self.price_wt and not self.is_checked) or not self.price_wt


class NumberOrderItem(OrderItem):
    number = models.IntegerField()


class WorkingTime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


# Delete files not only db object
@receiver(pre_delete, sender=FileOrderItem)
def fileorderitem_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
