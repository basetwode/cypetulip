from decimal import Decimal

from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import TestCase, AsyncRequestFactory

from shop.models.accounts import Contact, Company
from shop.models.orders import OrderState, OrderDetail, OrderItem
from shop.models.products import ProductSubItem
from .views.main import AccountingView


class AccountingViewTest(TestCase):
    url = '/accounting'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)
        initial_state = OrderState.objects.create(initial=True, name="Start")
        paid_state = OrderState.objects.create(initial=False, name="Paid", is_paid_state=True)
        sub_item = ProductSubItem.objects.create(price=10, price_on_request=False, name='product')
        order_open = OrderDetail.objects.create(company=self.contact.company, contact=self.contact, state=initial_state)
        OrderItem.objects.create(order_detail=order_open, price=10, tax_rate=0.19, product=sub_item, price_wt=11.9,
                                 price_discounted=10, price_discounted_wt=11.9)
        order_paid = OrderDetail.objects.create(company=self.contact.company, contact=self.contact, state=paid_state)
        OrderItem.objects.create(order_detail=order_paid, price=10, tax_rate=0.19, product=sub_item, price_wt=11.9,
                                 price_discounted=10, price_discounted_wt=11.9)

    def test_successful_login(self):
        request = self.factory.get(AccountingViewTest.url)
        request.user = self.admin
        response = AccountingView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(AccountingViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(AccountingViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)

    def test_elements_in_context_data(self):
        request = self.factory.get(AccountingViewTest.url)
        view = AccountingView()
        view.setup(request)
        view.object_list = view.get_queryset()

        context = view.get_context_data()
        self.assertIn('total_net', context)
        self.assertIn('total_gross', context)
        self.assertIn('counted_open_orders', context)
        self.assertIn('counted_open_payments', context)
        self.assertIn('counted_open_shipments', context)
        self.assertIn('last_orders', context)
        self.assertIn('open_order_state_id', context)
        self.assertIn('stock', context)

    def test_filter_in_context_data(self):
        request = self.factory.get(AccountingViewTest.url)
        view = AccountingView()
        view.setup(request)
        view.object_list = view.get_queryset()

        context = view.get_context_data()
        self.assertEqual(context.get('total_net'), Decimal('20.00'))
        self.assertEqual(context.get('total_gross'), Decimal('23.8'))
        self.assertEqual(context.get('counted_open_orders'), 1)
        self.assertEqual(context.get('counted_open_payments'), 0)
        self.assertEqual(context.get('counted_open_shipments'), 1)
        self.assertQuerysetEqual(context.get('last_orders'),OrderDetail.objects.all().order_by('-date_added')[:5])
        self.assertEqual(context.get('open_order_state_id'), 1)

    def _check_test_client_response(self, response, attribute, method_name):
        self.assertEqual(response.status_code, 200)
        self.assertIn(attribute, response.context_data)
        self.assertEqual(getattr(response.context_data[attribute], method_name)(), 1)
