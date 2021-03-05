from django.urls import reverse_lazy
# Create your views here.
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from permissions.mixins import LoginRequiredMixin
from shop.models.accounts import Employee


class EmployeeOverviewView(LoginRequiredMixin, ListView):
    template_name = 'management/employees/employees-overview.html'
    context_object_name = 'employees'
    model = Employee


class EmployeeCreationView(LoginRequiredMixin, CreateView):
    template_name = 'management/generic/generic-create.html'
    context_object_name = 'employee'
    model = Employee
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('employees_overview')
