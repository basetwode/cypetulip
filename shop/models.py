from datetime import datetime

from django.contrib.auth.models import User as DjangoUser
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from django.utils.translation import gettext_lazy as _
from tinymce import HTMLField

from billing.utils import calculate_sum
from mediaserver.upload import (company_files_upload_handler, fs, order_files_upload_handler,
                                public_files_upload_handler, rand_key)


class Company(models.Model):
    name = models.CharField(max_length=100)
    company_id = models.CharField(max_length=100, blank=True, null=True)
    term_of_payment = models.IntegerField(default=10)
    street = models.CharField(max_length=40, default=None)
    number = models.CharField(max_length=5, default=None)
    zipcode = models.CharField(max_length=5, default=None)
    city = models.CharField(max_length=30, default=None)
    logo = models.FileField(default=None, null=True, blank=True,
                            upload_to=company_files_upload_handler, storage=fs)

    class Meta:
        verbose_name_plural = "Companies"

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.company_id is None or len(self.company_id) == 0:
            self.company_id = rand_key(12)
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def __str__(self):
        return self.name


class Contact(DjangoUser):
    GENDER_CHOICES = (
        ('M', _('Male')),
        ('F', _('Female')),
        ('D', _('Others')),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    telephone = models.CharField(max_length=40)
    language = models.CharField(max_length=2, default='en')

    def __str__(self):
        return str(self.company) + ' - ' + self.last_name


class Address(models.Model):
    name = models.CharField(max_length=100)
    street = models.CharField(max_length=40, default=None)
    number = models.CharField(max_length=5, default=None)
    zipcode = models.CharField(max_length=5, default=None)
    city = models.CharField(max_length=100, default=None)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, default=None, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return self.contact.__str__() + " | " + self.name


class ProductCategory(models.Model):
    description = models.CharField(max_length=300)
    name = models.CharField(max_length=50)
    mother_category = models.ForeignKey(
        'self', on_delete=models.CASCADE, default=None, blank=True, null=True)
    child_categories = models.ManyToManyField('self', default=None, blank=True, symmetrical=False,
                                              related_name='ChildCategories')
    is_main_category = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, default=None)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)


# This is an orderable item which shows up when ordering a product that is public.
# like squaremeter notes on a plan


class ProductSubItem(models.Model):
    price = models.FloatField()
    special_price = models.FloatField(default=False, blank=True, null=True)
    price_on_request = models.BooleanField(default=False, blank=True, null=True)
    tax = models.FloatField(default=0.19, blank=False, null=False)
    name = models.CharField(max_length=30)
    description = HTMLField('Description')
    details = HTMLField('Details')
    requires_file_upload = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    is_multiple_per_item = models.BooleanField(default=False)
    is_once_per_order = models.BooleanField(default=False)

    def __str__(self):
        if hasattr(self, 'product'):
            return f"{self.product.category} | {self.name} ({self.product.get_stock()}) | {self.price} €"
        else:
            return f"{self.name} | {self.price}"

    def price_wt(self):
        return round(self.price * (1 + self.tax), 2)

    def special_price_wt(self):
        return round(self.special_price * (1 + self.tax), 2) if self.special_price else None

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
    name = models.CharField(max_length=50)
    select = models.ForeignKey(SelectSubItem, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# can be used for number of this item like 4 trousers
class NumberSubItem(ProductSubItem):
    pass
    # name = models.CharField(max_length=20)


# can be used for "as a present" or "moebliert" for example
class CheckBoxSubItem(ProductSubItem):
    pass
    # name = models.CharField(max_length=100)


'''
    State of a single order item eg. sent, going to be send, delivered
'''


class OrderItemState(models.Model):
    name = models.CharField(max_length=20)
    next_state = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='previous_state', )


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
    stock = models.IntegerField(default=0, blank=True, null=True)
    product_picture = models.ImageField(default=None, null=True, blank=True,
                                        upload_to=public_files_upload_handler,
                                        storage=fs)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    is_public = models.BooleanField()
    assigned_sub_products = models.ManyToManyField(ProductSubItem, default=None, blank=True,
                                                   symmetrical=False,
                                                   related_name='sub_products')
    attributes = models.ManyToManyField(ProductAttributeTypeInstance, blank=True)

    def __str__(self):
        return self.name + ' - public ' + str(self.is_public)

    def decrease_stock(self):
        self.stock = self.stock - 1 if self.stock > 0 else self.stock
        self.save()

    def increase_stock(self):
        self.stock = self.stock + 1 if self.stock > -1 else self.stock
        self.save()

    def get_stock(self):
        return f"{self.stock if self.stock > -1 else '~'}"


class IndividualOffer(models.Model):
    date_added = models.DateTimeField(auto_now=True, blank=True)
    mail = models.EmailField()
    message = models.CharField(max_length=1000)
    contact = models.ForeignKey(Contact, null=True, blank=True, default=None, editable=False, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, editable=False, null=True, on_delete=models.SET_NULL)

    def is_new(self):
        return (datetime.now().date() - self.date_added.date()).days < 3


class Discount(models.Model):
    voucher_id = models.CharField(unique=True, max_length=20, default="VOUCHER")
    discount_percentage = models.FloatField(default=0)
    eligible_products = models.ManyToManyField(Product, blank=True, null=True)
    eligible_categories = models.ManyToManyField(ProductCategory, blank=True, null=True)
    valid_until_date = models.DateTimeField(blank=True, null=True)
    count = models.IntegerField(default=0)
    valid_until_count = models.IntegerField(default=-1)
    enabled = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now=True, blank=True)

    def discount_percentage_in_percent(self):
        return int(self.discount_percentage * 100)

    def is_invalid(self):
        is_expired = datetime.now() > self.valid_until_date
        is_utilized = self.count >= self.valid_until_count
        return is_expired or is_utilized or not self.enabled

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(Discount, self).save(force_insert, force_update, using, update_fields)


class Order(models.Model):
    order_id = models.IntegerField(null=True, blank=True)
    order_hash = models.CharField(max_length=30, null=True, blank=True)
    is_send = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, )
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
        Employee, on_delete=models.CASCADE, null=True, blank=True, )
    state = models.ForeignKey(OrderState, on_delete=models.CASCADE, null=True,
                              blank=True, )
    date_bill = models.DateTimeField(null=True, blank=True)
    bill_sent = models.BooleanField(default=False, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True, )
    shipment_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True,
                                         related_name='shipment_address')
    billing_address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name='billing_address')
    is_cancelled = models.BooleanField(default=False, blank=True, null=True, editable=False)
    discount = models.ForeignKey(Discount, default=None, blank=True, null=True, on_delete=models.SET_NULL)

    def unique_nr(self):
        return "CTNR" + str(self.id).rjust(10, "0")

    def send_order(self):
        self.date_added = datetime.now()
        self.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.__was_canceled():
            self.increase_stocks()
            self.is_cancelled = True
        elif self.__was_uncancelled():
            self.decrease_stocks()
            self.is_cancelled = False
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)
        if self.discount:
            self.apply_discount()
        else:
            self.remove_discount()

    def increase_stocks(self):
        for order_item in self.order.orderitem_set.all():
            if isinstance(order_item.product.product, Product):
                order_item.product.product.increase_stock()

    def decrease_stocks(self):
        for order_item in self.order.orderitem_set.all():
            if isinstance(order_item.product.product, Product):
                order_item.product.product.decrease_stock()

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
        return calculate_sum(self.orderitem_set, True, include_discount)

    def total(self, include_discount=False):
        return calculate_sum(self.orderitem_set, False, include_discount)

    def total_discounted(self):
        return self.total(True)

    def total_discounted_wt(self):
        return self.total_wt(True)

    def total_discount(self):
        return round(self.total() - self.total_discounted(), 2)

    def total_discount_wt(self):
        return round(self.total_wt() - self.total_discounted_wt(), 2)


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
    price = models.FloatField(default=None, blank=True, null=True)
    price_wt = models.FloatField(default=None, blank=True, null=True)
    price_discounted = models.FloatField(default=None, blank=True, null=True)
    price_discounted_wt = models.FloatField(default=None, blank=True, null=True)
    applied_discount = models.FloatField(default=None, blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, recalculate_tax=False):

        if not self.price_wt and self.product and not self.product.price_on_request:
            self.price = self.product.special_price if self.product.special_price else self.product.price
            self.price_wt = self.product.bprice_wt()
        if self.product.price_on_request and not self.price_wt:
            self.price_wt = round(self.price * (1 + self.product.tax), 2)
        if not self.order_detail.state.is_sent_state:
            self.apply_discount_if_eligible()
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)
        for order_item in OrderItem.objects.filter(order_item=self):
            order_item.save()

    def delete(self, using=None, keep_parents=False):
        if hasattr(self.product, 'product'):
            self.product.product.increase_stock()
        super(OrderItem, self).delete(using, keep_parents)

    def is_discount_eligible(self):
        if not self.order_detail.discount:  # or self.applied_discount:
            return False
        product_id_in_discount = self.order_detail.discount.eligible_products.filter(id=self.product.id).exists()
        parent_product_in_discount = self.product.product.assigned_sub_products.filter(id=self.product.id).exists() if \
            hasattr(self.product, 'product') else False
        product_category_in_discount = self.order_detail.discount.eligible_categories.filter(
            id=self.product.product.category.id).exists() \
            if hasattr(self.product, 'product') else False
        is_parent_item_eligible = self.order_item.is_discount_eligible() if self.order_item else False
        return product_id_in_discount or parent_product_in_discount or product_category_in_discount or is_parent_item_eligible

    def apply_discount_if_eligible(self):
        if self.is_discount_eligible():
            self.applied_discount = round(self.price * self.order_detail.discount.discount_percentage, 2)
            self.price_discounted = round(self.price - self.applied_discount, 2)
            self.price_discounted_wt = round(self.price_discounted * (1 + self.product.tax), 2)

            return True
        self.applied_discount = 0
        self.price_discounted = self.price
        self.price_discounted_wt = self.price_wt
        return False

    def __str__(self):
        return f"{self.count}x {self.product.name if self.product else ''} {self.price}"

    def total_wt(self, include_discount=False):
        sub_items = OrderItem.objects.filter(order_item=self)
        return calculate_sum(sub_items, True, include_discount) + (
            self.price_wt if not include_discount else self.price_discounted_wt) \
            if sub_items.count() > 0 else 0 + self.price_wt if not include_discount else self.price_discounted_wt

    def total(self, include_discount=False):
        sub_items = OrderItem.objects.filter(order_item=self)
        return calculate_sum(sub_items, False, include_discount) + (
            self.price if not include_discount else self.price_discounted) \
            if sub_items.count() > 0 else 0 + self.price if not include_discount else self.price_discounted

    def total_discounted(self):
        return self.total(True)

    def total_discounted_wt(self):
        return self.total_wt(True)

    def total_discount(self):
        return round(self.total() - self.total_discounted(), 2)

    def total_discount_wt(self):
        return round(self.total_wt() - self.total_discounted_wt(), 2)


# Corresponding OrderItems for the subproducts
class FileOrderItem(OrderItem):
    file = models.FileField(default=None, null=True,
                            upload_to=order_files_upload_handler,
                            storage=fs)
    file_name = models.CharField(max_length=40, blank=True)


class SelectOrderItem(OrderItem):
    selected_item = models.ForeignKey(SelectItem, on_delete=models.CASCADE)


class CheckBoxOrderItem(OrderItem):
    is_checked = models.BooleanField()


class NumberOrderItem(OrderItem):
    number = models.IntegerField()


class WorkingTime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


# Delete files not only db object
@receiver(pre_delete, sender=FileOrderItem)
def fileorderitem_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
