from rest_framework import serializers, viewsets

from .models import Customer, Return, ReturnItem, Sale, SaleItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = "__all__"


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]


class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = "__all__"


class ReturnSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, read_only=True)

    class Meta:
        model = Return
        fields = "__all__"
        read_only_fields = ["created_by", "created_at"]


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related("customer", "warehouse")
    serializer_class = SaleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        customer_id = self.request.query_params.get("customer")
        warehouse_id = self.request.query_params.get("warehouse")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")

        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        if date_from:
            queryset = queryset.filter(sale_date__gte=date_from)

        if date_to:
            queryset = queryset.filter(sale_date__lte=date_to)

        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.select_related("sale", "printer")
    serializer_class = SaleItemSerializer


class ReturnViewSet(viewsets.ModelViewSet):
    queryset = Return.objects.select_related("sale", "customer", "warehouse")
    serializer_class = ReturnSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReturnItemViewSet(viewsets.ModelViewSet):
    queryset = ReturnItem.objects.select_related("ret", "printer")
    serializer_class = ReturnItemSerializer
