from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import VitaminLogForm
from .models import VitaminLog
from .services import build_tracking_summary


class OwnerVitaminLogMixin(LoginRequiredMixin):
    model = VitaminLog

    def get_queryset(self):
        return VitaminLog.objects.filter(user=self.request.user).order_by("-logged_for", "-created_at")


class VitaminLogListView(OwnerVitaminLogMixin, ListView):
    template_name = "tracking/list.html"
    context_object_name = "logs"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary"] = build_tracking_summary(self.request.user)
        return context


class VitaminLogCreateView(LoginRequiredMixin, CreateView):
    model = VitaminLog
    form_class = VitaminLogForm
    template_name = "tracking/form.html"
    success_url = reverse_lazy("tracking:index")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Vitamin log entry created.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_mode"] = "create"
        return context


class VitaminLogUpdateView(OwnerVitaminLogMixin, UpdateView):
    form_class = VitaminLogForm
    template_name = "tracking/form.html"
    success_url = reverse_lazy("tracking:index")

    def form_valid(self, form):
        messages.success(self.request, "Vitamin log entry updated.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_mode"] = "edit"
        return context


class VitaminLogDeleteView(OwnerVitaminLogMixin, DeleteView):
    template_name = "tracking/confirm_delete.html"
    success_url = reverse_lazy("tracking:index")

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, "Vitamin log entry deleted.")
        return super().delete(request, *args, **kwargs)
