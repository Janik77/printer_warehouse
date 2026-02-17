from django.conf import settings
from django.db import models

from inventory.models import Printer, Warehouse


class Customer(models.Model):
    full_name = models.CharField(max_length=160, verbose_name="ФИО")
    phone = models.CharField(max_length=40, blank=True, verbose_name="Телефон")
    iin_bin = models.CharField(max_length=20, blank=True, verbose_name="ИИН/БИН")
    company = models.CharField(max_length=160, blank=True, verbose_name="Компания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.full_name


class Sale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="sales", verbose_name="Клиент")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="sales", verbose_name="Склад")
    sale_date = models.DateField(verbose_name="Дата продажи")
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Сумма")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Создал")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["-sale_date", "-created_at"]
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"

    def __str__(self):
        return f"Продажа #{self.id} — {self.customer}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items", verbose_name="Продажа")
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT, verbose_name="Принтер")
    qty = models.IntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Сумма")

    class Meta:
        verbose_name = "Позиция продажи"
        verbose_name_plural = "Позиции продажи"

    def __str__(self):
        return f"{self.printer.serial_number} x{self.qty}"


class Return(models.Model):
    sale = models.ForeignKey(Sale, null=True, blank=True, on_delete=models.SET_NULL, related_name="returns", verbose_name="Продажа")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="returns", verbose_name="Клиент")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="returns", verbose_name="Склад")
    return_date = models.DateField(verbose_name="Дата возврата")
    reason = models.CharField(max_length=255, blank=True, verbose_name="Причина")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Создал")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        ordering = ["-return_date", "-created_at"]
        verbose_name = "Возврат"
        verbose_name_plural = "Возвраты"

    def __str__(self):
        return f"Возврат #{self.id} — {self.customer}"


class ReturnItem(models.Model):
    ret = models.ForeignKey(Return, on_delete=models.CASCADE, related_name="items", verbose_name="Возврат")
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT, verbose_name="Принтер")
    qty = models.IntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Цена")

    class Meta:
        verbose_name = "Позиция возврата"
        verbose_name_plural = "Позиции возврата"

    def __str__(self):
        return f"{self.printer.serial_number} x{self.qty}"
