from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import TestCase, AsyncRequestFactory

from management.models.main import LegalSetting, MailSetting, ShopSetting, CacheSetting
from shop.models.accounts import Contact, Company
from .models.main import Page
from .views.main import LegalView, CSSSettingsView, GenericView, \
    PermissionDeniedView, ContactView, GBTView, CancellationPolicyView, \
    PrivacyPolicyView


class LegalViewTest(TestCase):
    url = '/cms/legal'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)

    def test_successful_login(self):
        request = self.factory.get(LegalViewTest.url)
        request.user = self.admin
        response = LegalView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(LegalViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(LegalViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)


class CSSSettingsViewTest(TestCase):
    url = '/cms/css-setting'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)

    def test_successful_login(self):
        request = self.factory.get(CSSSettingsViewTest.url)
        request.user = self.admin
        response = CSSSettingsView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(CSSSettingsViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(CSSSettingsViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)

    def test_post_csssetting_form(self):
        request = self.factory.post(CSSSettingsViewTest.url + '1',
                                    data={})
        request.user = self.admin
        response = CSSSettingsView.as_view()(request)

        self.assertEqual(response.status_code, 200)


class GenericViewTest(TestCase):
    url = '/cms/home/'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)
        Page.objects.create(page_id=1, page_name='home')
        LegalSetting.objects.create(company_name='Test')
        CacheSetting.objects.create()

    def test_successful_login(self):
        request = self.factory.get(GenericViewTest.url)
        request.LANGUAGE_CODE = 'en'
        request.user = self.admin
        response = GenericView.as_view()(request, 'home')

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(GenericViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(GenericViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)

    def test_page_not_found(self):
        request = self.factory.get('/cms/not-found')
        request.LANGUAGE_CODE = 'en'
        request.user = self.admin
        response = GenericView.as_view()(request, 'not-found')

        self.assertEqual(response.status_code, 404)


class PermissionDeniedViewTest(TestCase):
    url = '/cms/test'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)

    def test_successful_login(self):
        request = self.factory.get(PermissionDeniedViewTest.url)
        request.user = self.admin
        response = PermissionDeniedView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(PermissionDeniedViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(PermissionDeniedViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)


class ContactViewTest(TestCase):
    url = '/cms/contact'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)
        MailSetting.objects.create(smtp_user='user', smtp_server='localhost',
                                   smtp_port=587, smtp_password='password', stmp_use_tls=True)

        ShopSetting.objects.create(google_recaptcha_publickey='pub', google_recaptcha_privatekey='priv')

    def test_successful_login(self):
        request = self.factory.get(ContactViewTest.url)
        request.user = self.admin
        response = ContactView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(ContactViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(ContactViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)

    def test_post_contact_form(self):
        request = self.factory.post(ContactViewTest.url, data={'name': 'test_user', 'email': 'test@test.com',
                                                               'phone': '088/2654789', 'message': 'This is a message'})
        response = ContactView.as_view()(request)

        self.assertEqual(response.status_code, 200)


class GBTViewTest(TestCase):
    url = '/cms/general-business-terms'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)
        LegalSetting.objects.create()

    def test_successful_login(self):
        request = self.factory.get(GBTViewTest.url)
        request.user = self.admin
        response = GBTView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(GBTViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(GBTViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)


class CancellationPolicyViewTest(TestCase):
    url = '/cms/cancellation-policy'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)
        LegalSetting.objects.create()

    def test_successful_login(self):
        request = self.factory.get(CancellationPolicyViewTest.url)
        request.user = self.admin
        response = CancellationPolicyView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(CancellationPolicyViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(CancellationPolicyViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)


class PrivacyPolicyViewTest(TestCase):
    url = '/cms/privacy-policy'

    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.admin = User.objects.create_user(
            username='admin', email='', password='admin')
        self.admin.is_superuser = True
        self.company = Company.objects.create(name='Company', street='street', number='1', zipcode='12345', city='city')
        self.contact = Contact.objects.create(
            username='user', email='', password='user', company=self.company)
        LegalSetting.objects.create()

    def test_successful_login(self):
        request = self.factory.get(PrivacyPolicyViewTest.url)
        request.user = self.admin
        response = PrivacyPolicyView.as_view()(request)

        self.assertEqual(response.status_code, 200)

    def test_permission_denied_for_loggedin_user(self):
        request = self.factory.get(PrivacyPolicyViewTest.url)
        request.user = self.contact

        self.assertRaises(PermissionDenied)

    def test_permission_denied_for_anonymous_user(self):
        request = self.factory.get(PrivacyPolicyViewTest.url)
        request.user = AnonymousUser()

        self.assertRaises(PermissionDenied)
