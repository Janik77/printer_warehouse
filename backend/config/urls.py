from django.contrib import admin
from django.contrib.auth import views as auth_views
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
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("ui.urls")),
    path("api/", include(router.urls)),
]
