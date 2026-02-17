from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms import formset_factory

from inventory.models import Printer, StockMovement, Warehouse
from sales.models import Return, Sale


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            if isinstance(field.widget, forms.Select):
                css_class = "form-select"
            current = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{current} {css_class}".strip()


class DateInput(forms.DateInput):
    input_type = "date"


class WarehouseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "city", "address", "is_active"]


class PrinterForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Printer
        fields = [
            "sku",
            "name",
            "brand",
            "model",
            "serial_number",
            "category",
            "purchase_price",
            "sale_price",
            "status",
        ]


class PrinterFilterForm(BootstrapFormMixin, forms.Form):
    serial_number = forms.CharField(required=False, label="Серийный номер")
    status = forms.ChoiceField(required=False, choices=[("", "Все")] + list(Printer.Status.choices), label="Статус")
    warehouse = forms.ModelChoiceField(required=False, queryset=Warehouse.objects.all(), label="Склад")


class StockMovementForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "movement_type",
            "warehouse_from",
            "warehouse_to",
            "printer",
            "qty",
            "note",
        ]

    def clean(self):
        cleaned_data = super().clean()
        movement_type = cleaned_data.get("movement_type")
        warehouse_from = cleaned_data.get("warehouse_from")
        warehouse_to = cleaned_data.get("warehouse_to")

        if movement_type == StockMovement.Type.OUT and not warehouse_from:
            self.add_error("warehouse_from", "Для расхода нужно указать склад отправления.")
        if movement_type in [StockMovement.Type.IN, StockMovement.Type.RETURN] and not warehouse_to:
            self.add_error("warehouse_to", "Для прихода/возврата нужно указать склад получения.")
        if movement_type == StockMovement.Type.TRANSFER:
            if not warehouse_from:
                self.add_error("warehouse_from", "Для перемещения нужно указать склад отправления.")
            if not warehouse_to:
                self.add_error("warehouse_to", "Для перемещения нужно указать склад получения.")

        return cleaned_data


class SaleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["customer", "warehouse", "sale_date"]
        widgets = {"sale_date": DateInput()}


class ReturnForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Return
        fields = ["sale", "customer", "warehouse", "return_date", "reason"]
        widgets = {"return_date": DateInput()}


class SaleItemForm(BootstrapFormMixin, forms.Form):
    printer = forms.ModelChoiceField(queryset=Printer.objects.all(), required=False, label="Принтер")
    qty = forms.IntegerField(min_value=1, required=False, label="Количество")
    price = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12, required=False, label="Цена")

    def clean(self):
        cleaned_data = super().clean()
        printer = cleaned_data.get("printer")
        qty = cleaned_data.get("qty")
        price = cleaned_data.get("price")

        if printer or qty or price:
            if not printer:
                self.add_error("printer", "Укажите принтер.")
            if not qty:
                self.add_error("qty", "Укажите количество.")
            if price is None:
                self.add_error("price", "Укажите цену.")

        return cleaned_data


class ReturnItemForm(BootstrapFormMixin, forms.Form):
    printer = forms.ModelChoiceField(queryset=Printer.objects.all(), required=False, label="Принтер")
    qty = forms.IntegerField(min_value=1, required=False, label="Количество")
    price = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12, required=False, label="Цена")

    def clean(self):
        cleaned_data = super().clean()
        printer = cleaned_data.get("printer")
        qty = cleaned_data.get("qty")
        price = cleaned_data.get("price")

        if printer or qty or price:
            if not printer:
                self.add_error("printer", "Укажите принтер.")
            if not qty:
                self.add_error("qty", "Укажите количество.")
            if price is None:
                self.add_error("price", "Укажите цену.")

        return cleaned_data


SaleItemFormSet = formset_factory(SaleItemForm, extra=3, min_num=1, max_num=3, validate_min=True)
ReturnItemFormSet = formset_factory(ReturnItemForm, extra=3, min_num=1, max_num=3, validate_min=True)


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
