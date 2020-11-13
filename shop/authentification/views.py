from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import View, CreateView

from shop.authentification.forms import CompleteCompanyForm, SignUpForm
from shop.models import Contact, Order, OrderItem, Address, Company

__author__ = ''


class LoginView(View):
    template_name = 'authentification/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/shop/home')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        order_from_session = Order.objects.filter(session=request.session.session_key)
        order_items_from_order_session = []
        if order_from_session:
            order_items_from_order_session = OrderItem.objects.filter(order=order_from_session[0])
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
                    order_from_contact = Order.objects.filter(company=contact.company, is_send=False)
                    for item in order_items_from_order_session:
                        item.order = order_from_contact[0]
                        item.save()
                    order_from_session.delete()
                else:
                    order_from_session.session = request.session.session_key
                # language = contact[0].language
                # request.LANGUAGE_CODE = language

                if 'next' in request.POST:
                    next_site = request.POST['next']
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
                    return render(request, 'authentification/login.html', {'next': next_site, 'message': message})
                else:
                    return render(request, 'authentification/login.html', {'message': message})
            else:
                if 'next' in request.POST:
                    next_site = request.POST['next']
                    return render(request, 'authentification/login.html', {'next': next_site})
                return render(request, 'authentification/login.html')


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
    template_name = 'authentification/register.html'
    success_url = reverse_lazy('shop:my_account')

    def form_valid(self, form):
        user = form.save(commit=False)
        company = Company(name=user.email, term_of_payment=10, street="",number="",zipcode="",city="")
        company.save()
        user.company = company
        user.email = user.username
        user.save()
        user.groups.add(Group.objects.get(name="client supervisor"))
        email = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user_ = authenticate(username=email, password=raw_password)
        if not self.request.user.is_authenticated:
            login(self.request, user_)
        return super(RegisterView, self).form_valid(form)

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
        return render(request, 'authentification/register.html', {'form': form, 'buttonText': 'Complete Account'})
