from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class Warehouse(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.city} — {self.name}"


class Printer(models.Model):
    class Status(models.TextChoices):
        IN_STOCK = "IN_STOCK", "In stock"
        SOLD = "SOLD", "Sold"
        RETURNED = "RETURNED", "Returned"
        WRITTEN_OFF = "WRITTEN_OFF", "Written off"

    sku = models.CharField(max_length=64, blank=True)
    name = models.CharField(max_length=160)
    brand = models.CharField(max_length=80, blank=True)
    model = models.CharField(max_length=80, blank=True)
    serial_number = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=80, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_STOCK)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "brand", "model"]

    def __str__(self):
        return f"{self.serial_number} — {self.name}"


class StockBalance(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="balances")
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, related_name="balances")
    qty = models.IntegerField(default=0)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["warehouse", "printer"], name="uniq_balance_warehouse_printer")
        ]

    def __str__(self):
        return f"{self.warehouse}: {self.printer.serial_number} = {self.qty}"


class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = "IN", "IN"
        OUT = "OUT", "OUT"
        TRANSFER = "TRANSFER", "TRANSFER"
        RETURN = "RETURN", "RETURN"
        ADJUST = "ADJUST", "ADJUST"

    movement_type = models.CharField(max_length=12, choices=Type.choices)
    warehouse_from = models.ForeignKey(
        Warehouse, null=True, blank=True, on_delete=models.SET_NULL, related_name="movements_out"
    )
    warehouse_to = models.ForeignKey(
        Warehouse, null=True, blank=True, on_delete=models.SET_NULL, related_name="movements_in"
    )
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT, related_name="movements")
    qty = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    note = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_movements"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movement_type} {self.printer.serial_number} x{self.qty}"
