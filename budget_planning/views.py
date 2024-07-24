from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from .models import Plan, Notification
from .forms import PlanForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class PlanListView(ListView):
    model = Plan
    template_name = 'budget_planning/plan_list.html'

    def get_queryset(self):
        return Plan.objects.filter(user=self.request.user)

@method_decorator(login_required, name='dispatch')
class PlanCreateView(CreateView):
    model = Plan
    form_class = PlanForm
    template_name = 'budget_planning/add_plan.html'
    success_url = reverse_lazy('budget_planning:plan_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        if not form.instance.previous_balance:
            form.instance.previous_balance = 0.0
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class NotificationListView(TemplateView):
    template_name = 'budget_planning/notifications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notifications'] = Notification.objects.filter(user=self.request.user, is_read=False)
        return context

@method_decorator(login_required, name='dispatch')
class NotificationDeleteView(DeleteView):
    model = Notification
    template_name = 'budget_planning/notification_confirm_delete.html'
    success_url = reverse_lazy('budget_planning:notifications')

@method_decorator(login_required, name='dispatch')
class PlanDeleteView(DeleteView):
    model = Plan
    template_name = 'budget_planning/plan_confirm_delete.html'
    success_url = reverse_lazy('budget_planning:plan_list')