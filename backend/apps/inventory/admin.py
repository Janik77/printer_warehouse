from django.contrib import admin
from .models import Warehouse, Printer, StockBalance, StockMovement


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "city", "name", "is_active", "created_at")
    list_filter = ("city", "is_active")
    search_fields = ("city", "name")


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ("id", "serial_number", "name", "brand", "model", "status", "created_at")
    list_filter = ("status", "brand")
    search_fields = ("serial_number", "name", "brand", "model")


@admin.register(StockBalance)
class StockBalanceAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "printer", "qty")
    list_filter = ("warehouse",)
    search_fields = ("printer__serial_number", "printer__name")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("movement_type", "printer", "qty", "warehouse_from", "warehouse_to", "created_at")
    list_filter = ("movement_type", "warehouse_from", "warehouse_to")
    search_fields = ("printer__serial_number", "note")
