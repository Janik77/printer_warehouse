from django.contrib import admin
from .models import Customer, Sale, SaleItem, Return, ReturnItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "sale_date", "customer", "warehouse", "total", "created_at")
    list_filter = ("warehouse", "sale_date")
    search_fields = ("customer__full_name",)
    inlines = [SaleItemInline]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "company", "created_at")
    search_fields = ("full_name", "phone", "company")


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ("id", "return_date", "customer", "warehouse", "created_at")
    list_filter = ("warehouse", "return_date")
    search_fields = ("customer__full_name", "reason")
    inlines = [ReturnItemInline]
