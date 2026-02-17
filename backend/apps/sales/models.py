from django.conf import settings
from django.db import models

from inventory.models import Warehouse, Printer


class Customer(models.Model):
    full_name = models.CharField(max_length=160)
    phone = models.CharField(max_length=40, blank=True)
    iin_bin = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="sales")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="sales")
    sale_date = models.DateField()
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sale_date", "-created_at"]

    def __str__(self):
        return f"Sale #{self.id} — {self.customer}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT)
    qty = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.printer.serial_number} x{self.qty}"


class Return(models.Model):
    sale = models.ForeignKey(Sale, null=True, blank=True, on_delete=models.SET_NULL, related_name="returns")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="returns")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="returns")
    return_date = models.DateField()
    reason = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-return_date", "-created_at"]

    def __str__(self):
        return f"Return #{self.id} — {self.customer}"


class ReturnItem(models.Model):
    ret = models.ForeignKey(Return, on_delete=models.CASCADE, related_name="items")
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT)
    qty = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.printer.serial_number} x{self.qty}"
