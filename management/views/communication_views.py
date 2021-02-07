from django.views.generic import TemplateView, FormView

from management.flower import FlowerView


class CommmunicationView(TemplateView, FlowerView):
    template_name = 'management/communication/communication-log.html'
    paginate_by = 20

    # todo: detail views with buttons and edit data
    # todo: retry view
    # todo: results
    def get_context_data(self, **kwargs):
        page = int(self.request.GET['page']) if 'page' in self.request.GET else 0
        tasks = self.get_tasks(page, self.paginate_by)

        return {**{
            "tasks": tasks,
            "previous_page": page - 1 if page > 0 else 0,
            "curr_page": page,
            "next_page": page + 1 if len(tasks) > 0 and len(tasks) >= self.paginate_by else page,
        }, **super(CommmunicationView, self).get_context_data(**kwargs)}


class CommmunicationDetailView(FlowerView, TemplateView):
    template_name = 'management/communication/communication-log-detail.html'

    def __init__(self):
        super(CommmunicationDetailView, self).__init__()

    def get_context_data(self, **kwargs):
        page = int(self.request.GET['page']) if 'page' in self.request.GET else 0
        task = self.get_task_info(kwargs['uuid'])

        return {**{
            "task": task,
        }, **super(CommmunicationDetailView, self).get_context_data(**kwargs)}


class CommmunicationRetryView(FormView, FlowerView):
    template_name = 'management/communication/communication-log.html'
