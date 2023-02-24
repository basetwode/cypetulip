from datetime import datetime

from _decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.db.models import Sum, Q
from django.utils.translation import gettext_lazy as _
from tinymce.models import HTMLField

from mediaserver.upload import order_files_upload_handler, fs, public_files_upload_handler
from shop.models.accounts import Contact


class ProductCategory(models.Model):
    path = models.CharField(max_length=300, verbose_name=_('Path'), null=True, blank=True, db_index=True)
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
        verbose_name_plural = _('Categories')

    def build_path(self, path=""):
        return self.mother_category.build_path(
            self.name + ("-" + path if path else "")) if self.mother_category else self.name + (
            "-" + path if path else "")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.path = self.build_path()
        super(ProductCategory, self).save(force_insert, force_update, using, update_fields)


class ProductSubItem(models.Model):
    price = models.FloatField(verbose_name=_('Price'))
    special_price = models.FloatField(default=False, blank=True, null=True, verbose_name=_('Special price'))
    price_on_request = models.BooleanField(default=False, blank=True, null=True, verbose_name=_('Price on request'))
    tax = models.FloatField(default=0.19, blank=False, null=False, verbose_name=_('Tax'))
    name = models.CharField(max_length=30)
    description = HTMLField(_('Description'), blank=True, null=True)
    details = HTMLField(_('Details'), blank=True, null=True)
    requires_file_upload = models.BooleanField(default=False, verbose_name=_('Requires file upload'))
    is_required = models.BooleanField(default=False, verbose_name=_('Is required'))
    is_multiple_per_item = models.BooleanField(default=False, verbose_name=_('Is multiple per item'))
    is_once_per_order = models.BooleanField(default=False, verbose_name=_('Is once per order'))

    class Meta:
        verbose_name = _('ProductSubItem')
        verbose_name_plural = _('ProductSubItems')

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
    extensions = models.CharField(max_length=200, null=True, blank=True, default="")
    file = models.FileField(default=None, null=True, blank=True,
                            upload_to=order_files_upload_handler, storage=fs)

    class Meta:
        verbose_name = _('FileSubItem')
        verbose_name_plural = _('FileSubItems')


class FileExtensionItem(models.Model):
    extension = models.CharField(max_length=30)
    file = models.ForeignKey(FileSubItem, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('FileExtensionItem')
        verbose_name_plural = _('FileExtensionItems')


class SelectSubItem(ProductSubItem):
    class Meta:
        verbose_name = _('SelectSubItem')
        verbose_name_plural = _('SelectSubItems')


class SelectItem(models.Model):
    name = models.CharField(max_length=40)
    select = models.ForeignKey(SelectSubItem, on_delete=models.CASCADE)
    price = models.FloatField(verbose_name=_('Price'), default=0)
    tax = models.FloatField(default=0.19, blank=False, null=False, verbose_name=_('Tax'))

    class Meta:
        verbose_name = _('SelectItem')
        verbose_name_plural = _('SelectItems')

    def __str__(self):
        return self.name

    def price_wt(self):
        return Decimal(f"{self.price * (1 + self.tax)}") \
            .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class NumberSubItem(ProductSubItem):
    class Meta:
        verbose_name = _('NumberSubItem')
        verbose_name_plural = _('NumberSubItems')


class CheckBoxSubItem(ProductSubItem):
    class Meta:
        verbose_name = _('CheckBoxSubItem')
        verbose_name_plural = _('CheckBoxSubItems')


class ProductAttributeType(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        verbose_name = _('ProductAttributeType')
        verbose_name_plural = _('ProductAttributeTypes')

    def __str__(self):
        return self.name


class ProductAttributeGroup(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    attribute_type_group = models.ManyToManyField(ProductAttributeType, blank=True,
                                                  verbose_name=_('Attribute type groups'))

    class Meta:
        verbose_name = _('Product attribute group')
        verbose_name_plural = _('Product attribute groups')

    def __str__(self):
        return self.name


class ProductAttributeTypeInstance(models.Model):
    type = models.ForeignKey(ProductAttributeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ['type']
        verbose_name = _('ProductAttributeTypeInstance')
        verbose_name_plural = _('ProductAttributeTypeInstances')

    def __str__(self):
        return self.type.__str__() + " | " + self.value


class Product(ProductSubItem):
    stock = models.IntegerField(default=0, blank=True, null=True, verbose_name=_('Stock'))
    max_items_per_order = models.IntegerField(default=10, verbose_name=_('Maximum number of items per order'))
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    is_public = models.BooleanField()
    assigned_sub_products = models.ManyToManyField(ProductSubItem, default=None, blank=True,
                                                   symmetrical=False,
                                                   related_name='sub_products', verbose_name=_('Assigned sub products'))
    attributes = models.ManyToManyField(ProductAttributeTypeInstance, blank=True, verbose_name=_('Attributes'))
    attribute_types = models.ManyToManyField(ProductAttributeType, blank=True, verbose_name=_('Attribute types'))

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def decrease_stock(self, number_of_items=1):
        self.stock = self.stock - number_of_items if self.stock > 0 else self.stock
        self.save()

    def increase_stock(self, number_of_items=1):
        self.stock = self.stock + number_of_items if self.stock > -1 else self.stock
        self.save()

    def get_stock(self):
        return f"{self.stock if self.stock > -1 else '~'}"

    def is_stock_sufficient(self, order):
        order_items_count_with_product = order.orderitem_set.filter(product=self) \
                                             .aggregate(count=Sum('count'))['count'] or 0

        return self.stock == -1 or (
                self.stock > order_items_count_with_product), self.stock - order_items_count_with_product

    def product_picture(self):
        return self.productimage_set.first().product_picture if self.productimage_set.count() > 0 else None

    def get_also_bought_products(self):
        from django.db.models import Count
        from shop.models.orders import OrderItem
        from shop.models.orders import OrderDetail
        related_orderitems = OrderItem.objects.filter(
            order_detail__in=OrderDetail.objects.filter(orderitem__product=self),
            order_item__isnull=True).exclude(product=self).order_by('product')
        return Product.objects.all() \
            .annotate(ocount=Count('orderitem', filter=Q(orderitem__in=related_orderitems))) \
            .filter(ocount__gt=0) \
            .order_by('-ocount')

    def get_related_products(self):
        return Product.objects.filter(category=self.category).order_by('id')


class ProductImage(models.Model):
    order = models.IntegerField(default=0, blank=True)
    product_picture = models.ImageField(default=None, null=True, blank=True,
                                        upload_to=public_files_upload_handler,
                                        storage=fs, verbose_name=_('Product picture'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('ProductImage')
        verbose_name_plural = _('ProductImages')


class IndividualOffer(models.Model):
    date_added = models.DateTimeField(auto_now=True, blank=True)
    mail = models.EmailField()
    message = models.CharField(max_length=1000)
    contact = models.ForeignKey(Contact, null=True, blank=True, default=None, editable=False, on_delete=models.CASCADE,
                                verbose_name=_('Contact'))
    product = models.ForeignKey(Product, editable=False, null=True, on_delete=models.SET_NULL,
                                verbose_name=_('Product'))

    def __str__(self):
        return self.mail + ' | ' + self.message

    def is_new(self):
        return (datetime.now().date() - self.date_added.date()).days < 3

    class Meta:
        verbose_name = _('Individual offer')
        verbose_name_plural = _('Individual offers')
