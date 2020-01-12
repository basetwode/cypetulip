from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from mediaserver.upload import (company_files_upload_handler, fs, order_files_upload_handler,
                                public_files_upload_handler, rand_key)


class Company(models.Model):
    name = models.CharField(max_length=100)
    company_id = models.CharField(max_length=100, blank=True, null=True)
    term_of_payment = models.IntegerField()
    street = models.CharField(max_length=40, default=None)
    number = models.CharField(max_length=5, default=None)
    zipcode = models.CharField(max_length=5, default=None)
    city = models.CharField(max_length=30, default=None)
    logo = models.FileField(default=None, null=True, blank=True,
                            upload_to=company_files_upload_handler, storage=fs)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.company_id is None or len(self.company_id) == 0:
            self.company_id = rand_key(12)
        models.Model.save(self, force_insert, force_update,
                          using, update_fields)

    def __str__(self):
        return self.name


class Contact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=20)
    gender = models.CharField(max_length=20)
    telephone = models.CharField(max_length=40)
    email = models.EmailField()
    language = models.CharField(max_length=2, default='en')

    def __str__(self):
        return str(self.company) + ' - ' + self.last_name


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
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)


# This is an orderable item which shows up when ordering a product that is public.
# like squaremeter notes on a plan


class ProductSubItem(models.Model):
    price = models.FloatField()
    # special_price = models.FloatField(default=False)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=300)
    details = models.CharField(max_length=300)
    requires_file_upload = models.BooleanField(default=False)
    is_required = models.BooleanField(default=False)
    is_multiple_per_item = models.BooleanField(default=False)
    is_once_per_order = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ' - required ' + str(self.is_required)


class FileSubItem(ProductSubItem):
    # name = models.CharField(max_length=20)
    pass


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
    next_state = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='previous_state', )

    # todo states have corresponding actions that also need to be linked!

    def __str__(self):
        return self.name


# A product can be whatever one needs, like a plan or a surcharge or hours worked..


class Product(ProductSubItem):
    product_picture = models.FileField(default=None, null=True, blank=True,
                                       upload_to=public_files_upload_handler,
                                       storage=fs)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    is_public = models.BooleanField()
    assigned_sub_products = models.ManyToManyField(ProductSubItem, default=None, blank=True,
                                                   symmetrical=False,
                                                   related_name='sub_products')

    def __str__(self):
        return self.name + ' - public ' + str(self.is_public)


class Order(models.Model):
    order_id = models.IntegerField(null=True, blank=True)
    order_hash = models.CharField(max_length=30, null=True, blank=True)
    is_send = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    token = models.CharField(max_length=25, blank=True, null=True)

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

    def __str__(self):
        return str(self.order_id)


class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20)
    date_added = models.DateTimeField(auto_now_add=True)
    assigned_employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True, )
    state = models.ForeignKey(OrderState, on_delete=models.CASCADE, null=True,
                              blank=True, )
    date_bill = models.DateTimeField(null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)


# Like a surcharge or discount or product or whatever.


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSubItem, on_delete=models.CASCADE)
    order_item = models.ForeignKey(
        'OrderItem', on_delete=models.CASCADE, null=True, blank=True, )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True, )
    additional_text = models.CharField(max_length=200, null=True, blank=True)
    state = models.ForeignKey(
        OrderItemState, on_delete=models.CASCADE, null=True, blank=True, )
    count = models.IntegerField(default=1)


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


class Discount(models.Model):
    pass


class WorkingTime(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


# Delete files not only db object
@receiver(pre_delete, sender=FileOrderItem)
def fileorderitem_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.file.delete(False)
