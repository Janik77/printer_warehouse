from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint


class Warehouse(models.Model):
    name = models.CharField(max_length=120, verbose_name="Название")
    city = models.CharField(max_length=120, verbose_name="Город")
    address = models.CharField(max_length=255, blank=True, verbose_name="Адрес")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["city", "name"]
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return f"{self.city} — {self.name}"


class Printer(models.Model):
    class Status(models.TextChoices):
        IN_STOCK = "IN_STOCK", "На складе"
        SOLD = "SOLD", "Продан"
        RETURNED = "RETURNED", "Возвращен"
        WRITTEN_OFF = "WRITTEN_OFF", "Списан"

    sku = models.CharField(max_length=64, blank=True, verbose_name="SKU")
    name = models.CharField(max_length=160, verbose_name="Наименование")
    brand = models.CharField(max_length=80, blank=True, verbose_name="Бренд")
    model = models.CharField(max_length=80, blank=True, verbose_name="Модель")
    serial_number = models.CharField(max_length=80, unique=True, verbose_name="Серийный номер")
    category = models.CharField(max_length=80, blank=True, verbose_name="Категория")
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Цена закупки")
    sale_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Цена продажи")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_STOCK, verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["-created_at", "brand", "model"]
        verbose_name = "Принтер"
        verbose_name_plural = "Принтеры"

    def __str__(self):
        return f"{self.serial_number} — {self.name}"


class StockBalance(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="balances", verbose_name="Склад")
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, related_name="balances", verbose_name="Принтер")
    qty = models.IntegerField(default=0, verbose_name="Количество")

    class Meta:
        constraints = [
            UniqueConstraint(fields=["warehouse", "printer"], name="uniq_balance_warehouse_printer")
        ]
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.warehouse}: {self.printer.serial_number} = {self.qty}"


class StockMovement(models.Model):
    class Type(models.TextChoices):
        IN = "IN", "Приход"
        OUT = "OUT", "Расход"
        TRANSFER = "TRANSFER", "Перемещение"
        RETURN = "RETURN", "Возврат"
        ADJUST = "ADJUST", "Корректировка"

    movement_type = models.CharField(max_length=12, choices=Type.choices, verbose_name="Тип перемещения")
    warehouse_from = models.ForeignKey(
        Warehouse, null=True, blank=True, on_delete=models.SET_NULL, related_name="movements_out", verbose_name="Со склада"
    )
    warehouse_to = models.ForeignKey(
        Warehouse, null=True, blank=True, on_delete=models.SET_NULL, related_name="movements_in", verbose_name="На склад"
    )
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT, related_name="movements", verbose_name="Принтер")
    qty = models.IntegerField(verbose_name="Количество")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Цена за единицу")
    note = models.CharField(max_length=255, blank=True, verbose_name="Примечание")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="stock_movements", verbose_name="Создал"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Перемещение"
        verbose_name_plural = "Перемещения"

    def __str__(self):
        return f"{self.movement_type} {self.printer.serial_number} x{self.qty}"
