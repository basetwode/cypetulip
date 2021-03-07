import csv
import secrets

from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic.edit import UpdateView, FormView
from django_filters.views import FilterView

from management.forms.forms import ContactUserForm, ContactUserIncludingPasswordForm, ContactUserUpdatePasswordForm, \
    MergeAccountsForm, CustomerImportForm
from management.models.models import LegalSetting
from management.views.mixins import NotifyNewCustomerAccountView
from permissions.views.mixins import LoginRequiredMixin
from shop.filters.filters import ContactFilter
from shop.models.orders import Order, OrderDetail
from shop.models.accounts import Company, Contact, Address
from shop.views.mixins import WizardView, RepeatableWizardView
from utils.mixins import PaginatedFilterViews


class CustomersOverview(LoginRequiredMixin, PaginatedFilterViews, FilterView):
    template_name = 'management/customers/customers-overview.html'
    model = Contact
    paginate_by = 20
    ordering = ['company__customer_nr', 'company_customer_nr']
    filterset_class = ContactFilter


class CompanyCreationView(SuccessMessageMixin, LoginRequiredMixin, WizardView):
    page_title = _('Create Company')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Company
    fields = ['name', 'term_of_payment', 'street', 'number', 'zipcode', 'city', 'logo']
    success_message = _("Company created successfully")

    def get_back_url(self):
        return reverse_lazy('management_index')

    def get_success_url(self):
        return reverse_lazy('contact_create_view', kwargs={'id': '', 'parent_id': self.object.id})


class CompanyDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Company
    slug_field = 'id'
    slug_url_kwarg = "url_param"
    template = ''
    success_message = _("Company deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('customers_overview')


class ContactCreationView(SuccessMessageMixin, LoginRequiredMixin, RepeatableWizardView, NotifyNewCustomerAccountView):
    page_title = _('Create new contact')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Contact
    pk_url_kwarg = 'id'
    parent_key = 'company'
    self_url = 'contact_create_view'
    delete_url = 'contact_delete_view'
    requires_selection_on_next = True
    text_add_item = _("Add contact")
    text_select_item = _("Select a contact to edit")

    def get_back_url(self):
        return reverse_lazy('company_create_view', kwargs={'id': self.get_parent_id()})

    def get_next_url(self):
        return reverse_lazy('address_create_view', kwargs={'id': '',
                                                           'parent_id': self.get_object().id if self.get_object() else '0'})

    def get_success_url(self):
        return reverse_lazy('contact_create_view', kwargs={'id': '', 'parent_id': self.get_parent_id()})

    def get_form_class(self):
        if self.get_object():
            return ContactUserForm
        else:
            return ContactUserIncludingPasswordForm

    def form_valid(self, form):
        contact = form.save(commit=False)
        contact.company = Company.objects.get(id=self.get_parent_id())
        contact.username = contact.email
        contact.save()
        if 'notify_customer' in form.cleaned_data and form.cleaned_data['notify_customer']:
            self.notify_client(_("Your account at ") + LegalSetting.objects.first().company_name, contact,
                               form.cleaned_data['new_password1'])

        group = Group.objects.get(name="client")
        group.user_set.add(contact)
        if form.cleaned_data['is_client_supervisor']:
            sgroup = Group.objects.get(name='client supervisor')
            sgroup.user_set.add(contact)
        else:
            sgroup = Group.objects.get(name='client supervisor')
            sgroup.user_set.remove(contact)

        return super(ContactCreationView, self).form_valid(form)

    def get_initial(self):
        initial = super(ContactCreationView, self).get_initial()
        initial['is_client_supervisor'] = self.object.groups.filter(name='client supervisor').exists() \
            if self.object else False
        initial['notify_customer'] = False if self.object else True
        gen_password = secrets.token_urlsafe(10)
        initial['new_password1'] = gen_password
        initial['new_password2'] = gen_password
        return initial


class ContactResetPwdView(SuccessMessageMixin, LoginRequiredMixin, UpdateView, NotifyNewCustomerAccountView):
    template_name = 'management/generic/generic-edit.html'
    model = Contact
    form_class = ContactUserUpdatePasswordForm
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy('customers_overview')

    def get_initial(self):
        initial = super(ContactResetPwdView, self).get_initial()
        initial['notify_customer'] = True
        gen_password = secrets.token_urlsafe(10)
        initial['new_password1'] = gen_password
        initial['new_password2'] = gen_password
        return initial

    def form_valid(self, form):
        if 'notify_customer' in form.cleaned_data and form.cleaned_data['notify_customer']:
            self.notify_client(_("Your account at ") + LegalSetting.objects.first().company_name, self.get_object(),
                               form.cleaned_data['new_password1'])
        return super(ContactResetPwdView, self).form_valid(form)


class ContactDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Contact
    slug_field = 'id'
    pk_url_kwarg = 'id'
    template = ''
    success_message = _("Contact deleted successfully")

    def get_success_url(self, **kwargs):
        messages.success(self.request, self.success_message)

        return reverse_lazy('contact_create_view', kwargs={'id': '', 'parent_id': self.kwargs.get('parent_id')})


class AddressCreationView(SuccessMessageMixin, LoginRequiredMixin, RepeatableWizardView):
    page_title = _('Create new address')
    context_object_name = 'subitem'
    slug_field = 'id'
    slug_url_kwarg = 'id'
    model = Address
    fields = ['name', 'street', 'number', 'zipcode', 'city']
    pk_url_kwarg = 'id'
    parent_key = 'contact'
    self_url = 'address_create_view'
    delete_url = 'address_delete_view'
    text_add_item = _("Add address")
    text_select_item = _("Select an address to edit")

    def get_back_url(self):
        return reverse_lazy('contact_create_view', kwargs={'id': Contact.objects.get(id=self.get_parent_id()).id,
                                                           'parent_id': Contact.objects.get(
                                                               id=self.get_parent_id()).company.id})

    def get_next_url(self):
        return reverse_lazy('management_index')

    def get_success_url(self):
        return reverse_lazy('address_create_view', kwargs={'id': '', 'parent_id': self.get_parent_id()})

    def form_valid(self, form):
        address = form.save(commit=False)
        address.contact = Contact.objects.get(id=self.get_parent_id())
        address.save()
        return super(AddressCreationView, self).form_valid(form)


class AddressDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Address
    slug_field = 'id'
    pk_url_kwarg = 'id'
    template = ''
    success_message = _("Address deleted successfully")

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy('address_create_view')


class MergeAccounts(SuccessMessageMixin, LoginRequiredMixin, FormView, NotifyNewCustomerAccountView):
    form_class = MergeAccountsForm
    template_name = 'management/generic/generic-edit.html'
    success_url = reverse_lazy('customers_overview')

    def form_valid(self, form):
        contacts_to_merge = form.cleaned_data['contacts']
        contact_to_merge_to = form.cleaned_data['leading_contact']

        companies = Company.objects.filter(contact__in=contacts_to_merge)
        order_details = OrderDetail.objects.filter(contact__in=contacts_to_merge)
        addresses = Address.objects.filter(contact__in=contacts_to_merge)

        order_details.update(contact=contact_to_merge_to, company=contact_to_merge_to.company, session="")
        addresses.update(contact=contact_to_merge_to)
        # todo: merge addresses to remove dups
        contacts_to_merge.delete()
        companies.delete()

        messages.success(self.request, _("Merge done") + " | " +
                         str(contacts_to_merge.count()) + "Accounts, " + str(order_details.count()) + "orders")

        if not contact_to_merge_to.is_registered():
            contact_to_merge_to.username = contact_to_merge_to.email
            password = secrets.token_urlsafe(10)
            contact_to_merge_to.set_password(password)
            contact_to_merge_to.save()
            self.notify_client(_("Your account at ") + LegalSetting.objects.first().company_name, contact_to_merge_to,
                               password)

            group = Group.objects.get(name="client")
            group.user_set.add(contact_to_merge_to)
            sgroup = Group.objects.get(name='client supervisor')
            sgroup.user_set.add(contact_to_merge_to)

        return super(MergeAccounts, self).form_valid(form)

    def get_initial(self):
        initial = super(MergeAccounts, self).get_initial()
        initial['notify_customer'] = True
        return initial

    def get_form_kwargs(self):
        form_kwargs = super(MergeAccounts, self).get_form_kwargs()
        return {**form_kwargs, **{'contact': Contact.objects.get(id=self.kwargs['id'])}}


class CustomerImportView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'management/customers/customer-import.html'
    form_class = CustomerImportForm
    success_url = reverse_lazy('customers_overview')

    def form_valid(self, form):
        csv_reader = csv.DictReader(chunk.decode() for chunk in self.request.FILES["input_file"])
        count_successful_imports = 0
        errors = []

        for row in csv_reader:
            try:
                if not Contact.objects.filter(username=row["email"]).exists():
                    company = Company(name=row['company_name'], street=row['street'], number=row['number'],
                                      zipcode=row['zipcode'], city=row['city'])
                    company.save()
                    contact = Contact(company=company, gender=row['gender'], telephone=row['phone'], email=row["email"],
                                      username=row["email"], first_name=row['firstname'], last_name=row['lastname'],
                                      password=row['password'],
                                      language='de')
                    contact.save()
                    address = Address(name=row['street'] + " " + row['number'], street=row['street'],
                                      number=row['number'], zipcode=row['zipcode'], city=row['city'], contact=contact)
                    address.save()

                    group = Group.objects.get(name="client")
                    group.user_set.add(contact)
                    sgroup = Group.objects.get(name='client supervisor')
                    sgroup.user_set.add(contact)
                    count_successful_imports += 1
                else:
                    errors.append(_("User with mail %(mail)s already exists") % {'mail': row['email']})
            except Exception as e:
                errors.append(str(e))
        messages.success(self.request, _("Successfully imported %(total_success)s of %(total)s") %
                         {'total_success': str(count_successful_imports), 'total': csv_reader.line_num - 1})
        if len(errors) > 0:
            messages.error(self.request, ", ".join(errors))
        return super(CustomerImportView, self).form_valid(form)
