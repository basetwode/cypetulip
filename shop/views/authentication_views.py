from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordResetView
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import View, CreateView

from shop.forms.authentication_forms import CompleteCompanyForm, SignUpForm, PasswordResetFormSMTP
from shop.models.orders import Order
from shop.models.accounts import Company, Contact, Address

__author__ = ''


class LoginView(View):
    template_name = 'shop/authentication/authentication-login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/shop/home')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        order_from_session = Order.objects.filter(session=request.session.session_key, orderdetail__state__isnull=True)
        order_items_from_order_session = []
        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                auth_login(request, user)
                contact = Contact.objects.get(user_ptr=request.user)
                if contact:
                    order_from_contact = Order.objects.filter(company=contact.company, orderdetail__state__isnull=True)
                    if order_from_contact.count() == 0:
                        order_from_contact, order_detail = Order.create_new_order(request)
                    else:
                        order_from_contact = order_from_contact.first()
                    if order_from_session.count() > 0:
                        for item in order_from_session.first().orderitem_set.all():
                            item.order = order_from_contact
                            item.order_detail = order_from_contact.orderdetail_set.first()
                            item.save()
                    order_from_session.delete()
                else:
                    order_from_session.session = request.session.session_key
                # language = contact[0].language
                # request.LANGUAGE_CODE = language

                if 'next' in request.POST:
                    next_site = request.POST['next']
                    return HttpResponseRedirect(next_site)
                if 'next' in request.GET and len(request.GET['next']) > 0:
                    next_site = request.GET['next']
                    return HttpResponseRedirect(next_site)
                return HttpResponseRedirect('/cms/home')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your account is disabled.")

        else:
            message = 'Ihr Benutzername und/oder Passwort sind falsch. Versuchen Sie es erneut.'
            if message:
                if 'next' in request.POST:
                    next_site = request.POST['next']
                    return render(request, 'shop/authentication/authentication-login.html', {'next': next_site, 'message': message})
                else:
                    return render(request, 'shop/authentication/authentication-login.html', {'message': message})
            else:
                if 'next' in request.POST:
                    next_site = request.POST['next']
                    return render(request, 'shop/authentication/authentication-login.html', {'next': next_site})
                return render(request, 'shop/authentication/authentication-login.html')


class LogoutView(View):

    def get(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
        return HttpResponseRedirect('/shop/login')

    def post(self, request):
        auth_logout(request)
        return HttpResponseRedirect('/shop/login')


class RegisterView(CreateView):
    model = Contact
    form_class = SignUpForm
    template_name = 'shop/authentication/authentication-register.html'
    success_url = reverse_lazy('shop:my_account')

    def form_valid(self, form):
        order_from_session = Order.objects.filter(session=self.request.session.session_key, orderdetail__state__isnull=True)
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
            order.save()
            order_detail = order.orderdetail_set.first()
            order_detail.contact = contact
            order_detail.save()

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
