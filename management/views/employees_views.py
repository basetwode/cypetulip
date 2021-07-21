from django.urls import reverse_lazy
# Create your views here.
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from permissions.views.mixins import LoginRequiredMixin
from shop.models.accounts import Contact


class EmployeeOverviewView(LoginRequiredMixin, ListView):
    template_name = 'management/employees/employees-overview.html'
    context_object_name = 'employees'
    model = Contact

    def get_queryset(self):
        return super().get_queryset().filter(is_staff=True)


class EmployeeCreationView(LoginRequiredMixin, CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'employee'
    model = Contact
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('employees_overview')
