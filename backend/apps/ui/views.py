from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from inventory.models import Printer, StockBalance, StockMovement, Warehouse
from inventory.services import apply_movement
from sales.models import Return, Sale
from sales.services import create_return_with_items, create_sale_with_items

from .forms import (
    PrinterFilterForm,
    PrinterForm,
    ReturnForm,
    ReturnItemFormSet,
    SaleForm,
    SaleItemFormSet,
    StockMovementForm,
    WarehouseForm,
)


@login_required
def dashboard(request):
    balances = (
        StockBalance.objects.filter(qty__gt=0)
        .select_related("warehouse", "printer")
        .order_by("warehouse__name", "printer__name")
    )
    movements = StockMovement.objects.select_related("printer", "warehouse_from", "warehouse_to")[:20]
    sales = Sale.objects.select_related("customer", "warehouse")[:10]
    returns = Return.objects.select_related("customer", "warehouse")[:10]

    return render(
        request,
        "ui/dashboard.html",
        {
            "balances": balances,
            "movements": movements,
            "sales": sales,
            "returns": returns,
            "page_title": "Панель управления",
        },
    )


class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = "ui/warehouse_list.html"


class WarehouseCreateView(LoginRequiredMixin, CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = "ui/form.html"
    success_url = reverse_lazy("ui:warehouse_list")
    extra_context = {"page_title": "Создать склад", "submit_label": "Сохранить"}

    def form_valid(self, form):
        messages.success(self.request, "Склад успешно создан.")
        return super().form_valid(form)


class WarehouseUpdateView(LoginRequiredMixin, UpdateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = "ui/form.html"
    success_url = reverse_lazy("ui:warehouse_list")
    extra_context = {"page_title": "Редактировать склад", "submit_label": "Сохранить"}

    def form_valid(self, form):
        messages.success(self.request, "Склад успешно обновлён.")
        return super().form_valid(form)


class WarehouseDeleteView(LoginRequiredMixin, DeleteView):
    model = Warehouse
    template_name = "ui/confirm_delete.html"
    success_url = reverse_lazy("ui:warehouse_list")
    extra_context = {"page_title": "Удаление склада"}

    def form_valid(self, form):
        messages.success(self.request, "Склад успешно удалён.")
        return super().form_valid(form)


class PrinterListView(LoginRequiredMixin, ListView):
    model = Printer
    template_name = "ui/printer_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filter_form = PrinterFilterForm(self.request.GET or None)

        if self.filter_form.is_valid():
            serial_number = self.filter_form.cleaned_data.get("serial_number")
            status = self.filter_form.cleaned_data.get("status")
            warehouse = self.filter_form.cleaned_data.get("warehouse")

            if serial_number:
                queryset = queryset.filter(serial_number__icontains=serial_number)
            if status:
                queryset = queryset.filter(status=status)
            if warehouse:
                queryset = queryset.filter(balances__warehouse=warehouse).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = self.filter_form
        return context


class PrinterCreateView(LoginRequiredMixin, CreateView):
    model = Printer
    form_class = PrinterForm
    template_name = "ui/form.html"
    success_url = reverse_lazy("ui:printer_list")
    extra_context = {"page_title": "Создать принтер", "submit_label": "Сохранить"}

    def form_valid(self, form):
        messages.success(self.request, "Принтер успешно создан.")
        return super().form_valid(form)


class PrinterUpdateView(LoginRequiredMixin, UpdateView):
    model = Printer
    form_class = PrinterForm
    template_name = "ui/form.html"
    success_url = reverse_lazy("ui:printer_list")
    extra_context = {"page_title": "Редактировать принтер", "submit_label": "Сохранить"}

    def form_valid(self, form):
        messages.success(self.request, "Принтер успешно обновлён.")
        return super().form_valid(form)


class PrinterDeleteView(LoginRequiredMixin, DeleteView):
    model = Printer
    template_name = "ui/confirm_delete.html"
    success_url = reverse_lazy("ui:printer_list")
    extra_context = {"page_title": "Удаление принтера"}

    def form_valid(self, form):
        messages.success(self.request, "Принтер успешно удалён.")
        return super().form_valid(form)


class MovementListView(LoginRequiredMixin, ListView):
    model = StockMovement
    template_name = "ui/movement_list.html"


class MovementCreateView(LoginRequiredMixin, CreateView):
    model = StockMovement
    form_class = StockMovementForm
    template_name = "ui/form.html"
    success_url = reverse_lazy("ui:movement_list")
    extra_context = {"page_title": "Создать перемещение", "submit_label": "Сохранить"}

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        try:
            apply_movement(self.object)
        except ValueError as exc:
            self.object.delete()
            form.add_error(None, str(exc))
            messages.error(self.request, str(exc))
            return self.form_invalid(form)

        messages.success(self.request, "Перемещение успешно создано и применено.")
        return redirect(self.success_url)


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "ui/sale_list.html"


@login_required
def sale_create(request):
    if request.method == "POST":
        form = SaleForm(request.POST)
        formset = SaleItemFormSet(request.POST, prefix="items")
        if form.is_valid() and formset.is_valid():
            items = [f.cleaned_data for f in formset if f.cleaned_data.get("printer")]
            if not items:
                messages.error(request, "Добавьте хотя бы одну позицию продажи.")
            else:
                try:
                    sale = create_sale_with_items(
                        sale_data=form.cleaned_data,
                        items_data=items,
                        user=request.user,
                    )
                except ValueError as exc:
                    messages.error(request, str(exc))
                else:
                    messages.success(request, f"Продажа №{sale.id} успешно создана.")
                    return redirect("ui:sale_list")
        else:
            messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = SaleForm()
        formset = SaleItemFormSet(prefix="items")

    return render(
        request,
        "ui/sale_form.html",
        {"form": form, "formset": formset, "page_title": "Создать продажу", "submit_label": "Сохранить"},
    )


class ReturnListView(LoginRequiredMixin, ListView):
    model = Return
    template_name = "ui/return_list.html"


@login_required
def return_create(request):
    if request.method == "POST":
        form = ReturnForm(request.POST)
        formset = ReturnItemFormSet(request.POST, prefix="items")
        if form.is_valid() and formset.is_valid():
            items = [f.cleaned_data for f in formset if f.cleaned_data.get("printer")]
            if not items:
                messages.error(request, "Добавьте хотя бы одну позицию возврата.")
            else:
                try:
                    ret = create_return_with_items(
                        return_data=form.cleaned_data,
                        items_data=items,
                        user=request.user,
                    )
                except ValueError as exc:
                    messages.error(request, str(exc))
                else:
                    messages.success(request, f"Возврат №{ret.id} успешно создан.")
                    return redirect("ui:return_list")
        else:
            messages.error(request, "Исправьте ошибки в форме.")
    else:
        form = ReturnForm()
        formset = ReturnItemFormSet(prefix="items")

    return render(
        request,
        "ui/return_form.html",
        {"form": form, "formset": formset, "page_title": "Создать возврат", "submit_label": "Сохранить"},
    )
