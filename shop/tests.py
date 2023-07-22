from decimal import Decimal, ROUND_HALF_UP

from django.test import TestCase
# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from payment.models.main import Payment, PaymentDetail, PaymentMethod
from shop.models.accounts import Contact, Company
from shop.models.orders import OrderDetail, OrderItem, OrderState, PercentageDiscount
from shop.models.products import Product, ProductSubItem, ProductCategory


class OrderTestBase(TestCase):
    def setUp(self):
        self.cancelled_order_State = OrderState.objects.create(name="Cancelled")
        self.order_state = OrderState.objects.create(initial=True, name="Open",
                                                     cancel_order_state=self.cancelled_order_State)
        self.category = ProductCategory.objects.create(name="Test")
        sub_product = ProductSubItem.objects.create(price=2.91, tax=0.19, name="subproduct1")
        sub_product2 = ProductSubItem.objects.create(price=1.65, tax=0.19, name="subproduct2")
        product1 = Product.objects.create(price=10.98, tax=0.19, category=self.category,
                                          stock=10, is_public=True,
                                          name="product1")
        product_with_subproducts = Product.objects.create(price=13.98, tax=0.19,
                                                          stock=10, is_public=True, category=self.category,
                                                          name="product_with_subproducts")
        product_with_subproducts.assigned_sub_products.add(sub_product)
        product_with_subproducts.assigned_sub_products.add(sub_product2)

        product_specialprice = Product.objects.create(price=32.98, tax=0.09,
                                                      stock=1, is_public=True, category=self.category,
                                                      special_price=29.99,
                                                      name="product_specialprice")
        product_out_of_stock = Product.objects.create(price=10.98, tax=0.19,
                                                      stock=0, is_public=True, category=self.category,
                                                      name="product_out_of_stock")
        product_max_items = Product.objects.create(price=10.98, tax=0.19, is_public=True, category=self.category,
                                                   stock=10, max_items_per_order=1,
                                                   name="product_max_items")
        self.payment_method = PaymentMethod.objects.create(name="Bill")
        company = Company.objects.create(name="test company", street="", number="", zipcode="", city="")
        self.user = Contact.objects.create(username="test", password="test", company=company)

    def get_decimal_rounded(self, value):
        return Decimal(f"{value}").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class OrderUnitTest(OrderTestBase):

    def setUp(self):
        super(OrderUnitTest, self).setUp()
        self.product1 = Product.objects.get(name="product1")
        self.product2 = Product.objects.get(name="product_specialprice")
        self.product3 = Product.objects.get(name="product_with_subproducts")
        self.order = OrderDetail.objects.create(id=1)
        self.order_item1 = OrderItem.objects.create(order_detail=self.order, product=self.product1, count=2)
        self.order_item2 = OrderItem.objects.create(order_detail=self.order, product=self.product2, count=1)
        self.order_item3 = OrderItem.objects.create(order_detail=self.order, product=self.product3, count=1)
        self.suborderitem1 = OrderItem.objects.create(order_detail=self.order, order_item=self.order_item3,
                                                      product=self.product3.assigned_sub_products.get(
                                                          name="subproduct1"),
                                                      count=2)
        self.suborderitem2 = OrderItem.objects.create(order_detail=self.order, order_item=self.order_item3,
                                                      product=self.product3.assigned_sub_products.get(
                                                          name="subproduct2"),
                                                      count=1)

    def refresh(self):
        self.order.refresh_from_db()
        self.order_item1.refresh_from_db()
        self.order_item2.refresh_from_db()
        self.order_item3.refresh_from_db()
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.product3.refresh_from_db()

    def test_taxes_calculated_correctly_for_new_order(self):
        self.assertEqual(self.order_item1.get_subtotal_wt(), self.get_decimal_rounded(26.14),
                         "Orderitem 1 total equals 26.13")
        self.assertEqual(self.order_item2.get_subtotal_wt(), self.get_decimal_rounded(32.69),
                         "Orderitem 2 total equals 32.69")
        self.assertEqual(self.order_item3.get_subtotal_wt(), self.get_decimal_rounded(25.52),
                         "Orderitem 3 total equals 25.52")
        self.assertEqual(self.order.total_wt(), self.get_decimal_rounded(84.35), "Order total equals 84.35")

    def test_taxes_calculated_correctly_for_updated_order(self):
        self.refresh()
        self.order_item3.count = 2
        self.order_item3.save()
        self.assertEqual(self.order_item3.get_subtotal_wt(), self.get_decimal_rounded(51.04),
                         "Orderitem 3 total equals 51.04")
        self.assertEqual(self.order.total_wt(), self.get_decimal_rounded(109.87), "Order total equals 109.87")
        pass

    def test_percentagevoucher_correctly_applied(self):
        self.refresh()
        voucher = PercentageDiscount.objects.create(voucher_id="123", discount_percentage=0.1)
        voucher.eligible_categories.add(self.category)
        self.order.apply_voucher(voucher)
        self.refresh()
        self.assertEqual(self.order_item1.get_subtotal_wt(), self.get_decimal_rounded(23.52),
                         "Orderitem 1 total equals 23.52")
        self.assertEqual(self.order_item2.get_subtotal_wt(), self.get_decimal_rounded(29.42),
                         "Orderitem 2 total equals 29.42")
        self.assertEqual(self.order_item3.get_subtotal_wt(), self.get_decimal_rounded(22.97),
                         "Orderitem 3 total equals 22.97")
        self.assertEqual(self.order.total_wt(), self.get_decimal_rounded(75.91), "Order total equals 75.91")

    def test_product_stock_decreased_upon_sending_new_order(self):
        self.refresh()
        self.assertEqual(self.product1.stock, 10)
        self.assertEqual(self.product2.stock, 1)
        self.assertEqual(self.product3.stock, 10)
        self.order.state = self.order_state
        self.order.save()
        payment_detail = PaymentDetail.objects.create(order_detail=self.order, method=self.payment_method,
                                                      user=self.user)
        payment = Payment.objects.create(details=payment_detail, is_paid=False)
        self.refresh()
        self.assertEqual(self.product1.stock, 8)
        self.assertEqual(self.product2.stock, 0)
        self.assertEqual(self.product3.stock, 9)

    def test_product_stock_increased_upon_cancel_order(self):
        self.test_product_stock_decreased_upon_sending_new_order()
        self.order.state = self.cancelled_order_State
        self.order.save()
        self.refresh()
        self.assertEqual(self.product1.stock, 10)
        self.assertEqual(self.product2.stock, 1)
        self.assertEqual(self.product3.stock, 10)

    def test_orderamount_unchanged_when_sent_and_product_price_changes(self):
        self.refresh()
        self.order.state = self.order_state
        self.order.save()
        self.product1.price = 100.98 # was 10.98
        self.product1.tax = 0.49
        self.product1.save()
        self.order.save()
        self.assertEqual(self.order.total_wt(), self.get_decimal_rounded(84.35), "Order total equals 84.35")

    def test_orderamount_changed_when_notsent_and_product_price_changes(self):
        self.product1.price = 100.98 #was 10.98
        self.product1.tax = 0.23
        self.product1.save()
        self.refresh()
        self.order.save()
        self.assertEqual(self.order.total_wt(), self.get_decimal_rounded(306.63), "Order total equals 306.63")


class OrderRESTApiTest(APITestCase):

    def setUp(self):
        super(OrderRESTApiTest, self).setUp()
        self.client = APIClient()

    def test_asd(self):
        url = reverse('account-list')
        data = {'name': 'DabApps'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        self.assertEqual(Account.objects.get().name, 'DabApps')

# todo: view tests
