from django.views import View
from django.views.generic import CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin


class GenericCreateView(CreateView):
    page_name = "GenericView"
    page_info = "GenericView Info"

    def get_context_data(self, **kwargs):
        return {**{"page_name": self.page_name, "page_info": self.page_info},
                **super().get_context_data()}
