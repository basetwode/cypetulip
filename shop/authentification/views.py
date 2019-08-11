from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.generic import View
from shop.models import Contact

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

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                auth_login(request, user)

                contact = Contact.objects.filter(user=request.user)
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
                    return render(request, 'authentification/login.html', { 'next': next_site})
                return render(request, 'authentification/login.html')


class LogoutView(View):

    def get(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
        return HttpResponseRedirect('/shop/login')

    def post(self, request):
        auth_logout(request)
        return HttpResponseRedirect('/shop/login')