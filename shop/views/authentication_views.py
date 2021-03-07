from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetView, LoginView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.http import is_safe_url
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, CreateView, RedirectView

from shop.forms.authentication_forms import CompleteCompanyForm, SignUpForm, PasswordResetFormSMTP
from shop.models.orders import Order, OrderDetail
from shop.models.accounts import Company, Contact, Address

__author__ = ''


class LoginAuthenticationView(LoginView):
    template_name = 'shop/authentication/authentication-login.html'
    redirect_field_name = 'next'
    success_url = '/'

    def get_success_url(self):
        if not self.redirect_field_name in self.request.GET or len(self.request.GET[self.redirect_field_name])==0:
            redirect_to = self.success_url
        else:
            redirect_to = self.request.GET[self.redirect_field_name]
        return redirect_to

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        order_from_session = OrderDetail.objects.filter(session=self.request.session.session_key, state__isnull=True)
        contact = Contact.objects.filter(user_ptr=self.request.user)
        if contact.count()>0:
            contact = contact.first()
            order_from_contact = OrderDetail.objects.filter(company=contact.company, state__isnull=True)
            if order_from_contact.count() == 0:
                order_from_contact = OrderDetail.create_new_order(self.request)
            else:
                order_from_contact = order_from_contact.first()
            if order_from_session.count() > 0:
                for item in order_from_session.first().orderitem_set.all():
                    item.order = order_from_contact
                    item.order_detail = order_from_contact.orderdetail_set.first()
                    item.save()
            order_from_session.delete()
        else:
            order_from_session.session = self.request.session.session_key
        return super(LoginAuthenticationView, self).form_valid(form)


class LogoutView(RedirectView):
    url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            auth_logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class RegisterView(CreateView):
    model = Contact
    form_class = SignUpForm
    template_name = 'shop/authentication/authentication-register.html'
    success_url = reverse_lazy('shop:my_account')

    def form_valid(self, form):
        order_from_session = OrderDetail.objects.filter(session=self.request.session.session_key, state__isnull=True)
        user = form.save(commit=False)
        company = Company(name="", term_of_payment=10, street="",number="",zipcode="",city="")
        company.save()
        user.company = company
        user.email = user.username
        user.save()
        user.groups.add(Group.objects.get(name="client supervisor"))
        email = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user_ = authenticate(username=email, password=raw_password)
        if not self.request.user.is_authenticated:
            auth_login(self.request, user_)
        self.migrate_order(user, order_from_session )
        return HttpResponseRedirect(self.success_url)

    def migrate_order(self, contact, order_from_session):
        if order_from_session.count() > 0:
            order = order_from_session.first()
            order.company = contact.company
            order.contact = contact
            order.save()

    def get_context_data(self, **kwargs):
        return {**{'buttonText': _('Sign up')}, **super(RegisterView, self).get_context_data(**kwargs)}


class CompanyView(CompleteCompanyForm):

    def create(request):
        if request.user.is_authenticated:
            if request.method == 'POST':
                form = CompleteCompanyForm(request.POST)
                if form.is_valid():
                    company = form.save()
                    contact = Contact.objects.create(user=request.user, company=company,
                                                     first_name=request.user.first_name,
                                                     last_name=request.user.last_name, title='',
                                                     gender='', telephone='', email=request.user.email, language='de')
                    Address.objects.create(name='Standard', street=request.POST['street'],
                                           number=request.POST['number'], zipcode=request.POST['zipcode'],
                                           city=request.POST['city'],
                                           contact=contact)
                    return redirect('/cms/home')
            else:
                form = CompleteCompanyForm(initial={'term_of_payment': 10, 'name': request.user.username})
        else:
            return HttpResponseRedirect('/shop/login')
        return render(request, 'shop/authentication/authentication-register.html', {'form': form, 'buttonText': 'Complete Account'})


class PasswordResetViewSmtp(PasswordResetView):
    form_class = PasswordResetFormSMTP
