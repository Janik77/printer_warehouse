from django import forms
from django.forms import formset_factory

from inventory.models import Printer, StockMovement, Warehouse
from sales.models import Return, Sale


class DateInput(forms.DateInput):
    input_type = "date"


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ["name", "city", "address", "is_active"]


class PrinterForm(forms.ModelForm):
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


class PrinterFilterForm(forms.Form):
    serial_number = forms.CharField(required=False)
    status = forms.ChoiceField(required=False, choices=[("", "All")] + list(Printer.Status.choices))
    warehouse = forms.ModelChoiceField(required=False, queryset=Warehouse.objects.all())


class StockMovementForm(forms.ModelForm):
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
            self.add_error("warehouse_from", "warehouse_from is required for OUT")
        if movement_type in [StockMovement.Type.IN, StockMovement.Type.RETURN] and not warehouse_to:
            self.add_error("warehouse_to", "warehouse_to is required for IN/RETURN")
        if movement_type == StockMovement.Type.TRANSFER:
            if not warehouse_from:
                self.add_error("warehouse_from", "warehouse_from is required for TRANSFER")
            if not warehouse_to:
                self.add_error("warehouse_to", "warehouse_to is required for TRANSFER")

        return cleaned_data


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["customer", "warehouse", "sale_date"]
        widgets = {"sale_date": DateInput()}


class ReturnForm(forms.ModelForm):
    class Meta:
        model = Return
        fields = ["sale", "customer", "warehouse", "return_date", "reason"]
        widgets = {"return_date": DateInput()}


class SaleItemForm(forms.Form):
    printer = forms.ModelChoiceField(queryset=Printer.objects.all(), required=False)
    qty = forms.IntegerField(min_value=1, required=False)
    price = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12, required=False)

    def clean(self):
        cleaned_data = super().clean()
        printer = cleaned_data.get("printer")
        qty = cleaned_data.get("qty")
        price = cleaned_data.get("price")

        if printer or qty or price:
            if not printer:
                self.add_error("printer", "Printer is required.")
            if not qty:
                self.add_error("qty", "Qty is required.")
            if price is None:
                self.add_error("price", "Price is required.")

        return cleaned_data


class ReturnItemForm(forms.Form):
    printer = forms.ModelChoiceField(queryset=Printer.objects.all(), required=False)
    qty = forms.IntegerField(min_value=1, required=False)
    price = forms.DecimalField(min_value=0, decimal_places=2, max_digits=12, required=False)

    def clean(self):
        cleaned_data = super().clean()
        printer = cleaned_data.get("printer")
        qty = cleaned_data.get("qty")
        price = cleaned_data.get("price")

        if printer or qty or price:
            if not printer:
                self.add_error("printer", "Printer is required.")
            if not qty:
                self.add_error("qty", "Qty is required.")
            if price is None:
                self.add_error("price", "Price is required.")

        return cleaned_data


SaleItemFormSet = formset_factory(SaleItemForm, extra=3, min_num=1, validate_min=True)
ReturnItemFormSet = formset_factory(ReturnItemForm, extra=3, min_num=1, validate_min=True)
