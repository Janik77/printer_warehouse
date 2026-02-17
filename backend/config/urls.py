from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from inventory.api import PrinterViewSet, StockMovementViewSet, WarehouseViewSet
from sales.api import (
    CustomerViewSet,
    ReturnItemViewSet,
    ReturnViewSet,
    SaleItemViewSet,
    SaleViewSet,
)

router = DefaultRouter()
router.register(r"warehouses", WarehouseViewSet)
router.register(r"printers", PrinterViewSet)
router.register(r"movements", StockMovementViewSet)
router.register(r"customers", CustomerViewSet)
router.register(r"sales", SaleViewSet)
router.register(r"sale-items", SaleItemViewSet)
router.register(r"returns", ReturnViewSet)
router.register(r"return-items", ReturnItemViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
