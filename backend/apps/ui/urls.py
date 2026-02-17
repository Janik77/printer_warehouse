from django.urls import path

from . import views

app_name = "ui"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("warehouses/", views.WarehouseListView.as_view(), name="warehouse_list"),
    path("warehouses/create/", views.WarehouseCreateView.as_view(), name="warehouse_create"),
    path("warehouses/<int:pk>/edit/", views.WarehouseUpdateView.as_view(), name="warehouse_update"),
    path("warehouses/<int:pk>/delete/", views.WarehouseDeleteView.as_view(), name="warehouse_delete"),
    path("printers/", views.PrinterListView.as_view(), name="printer_list"),
    path("printers/create/", views.PrinterCreateView.as_view(), name="printer_create"),
    path("printers/<int:pk>/edit/", views.PrinterUpdateView.as_view(), name="printer_update"),
    path("printers/<int:pk>/delete/", views.PrinterDeleteView.as_view(), name="printer_delete"),
    path("movements/", views.MovementListView.as_view(), name="movement_list"),
    path("movements/create/", views.MovementCreateView.as_view(), name="movement_create"),
    path("sales/", views.SaleListView.as_view(), name="sale_list"),
    path("sales/create/", views.sale_create, name="sale_create"),
    path("returns/", views.ReturnListView.as_view(), name="return_list"),
    path("returns/create/", views.return_create, name="return_create"),
]
