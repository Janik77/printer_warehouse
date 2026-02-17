from django.db.models import Q
from rest_framework import serializers, viewsets

from .models import Printer, StockMovement, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"


class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Printer
        fields = "__all__"


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class PrinterViewSet(viewsets.ModelViewSet):
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        serial_number = self.request.query_params.get("serial")
        status_value = self.request.query_params.get("status")
        warehouse_id = self.request.query_params.get("warehouse")

        if serial_number:
            queryset = queryset.filter(serial_number__icontains=serial_number)

        if status_value:
            queryset = queryset.filter(status=status_value)

        if warehouse_id:
            queryset = queryset.filter(balances__warehouse_id=warehouse_id).distinct()

        return queryset


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.select_related("printer", "warehouse_from", "warehouse_to")
    serializer_class = StockMovementSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        movement_type = self.request.query_params.get("type")
        warehouse_id = self.request.query_params.get("warehouse")

        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        if movement_type:
            queryset = queryset.filter(movement_type=movement_type)

        if warehouse_id:
            queryset = queryset.filter(
                Q(warehouse_from_id=warehouse_id) | Q(warehouse_to_id=warehouse_id)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
