from decimal import Decimal

from django.db import transaction

from inventory.models import StockMovement
from inventory.services import apply_movement

from .models import Return, ReturnItem, Sale, SaleItem


@transaction.atomic
def create_sale_with_items(*, sale_data, items_data, user):
    sale = Sale.objects.create(created_by=user, total=Decimal("0.00"), **sale_data)
    total = Decimal("0.00")

    for item in items_data:
        subtotal = item["price"] * item["qty"]
        SaleItem.objects.create(
            sale=sale,
            printer=item["printer"],
            qty=item["qty"],
            price=item["price"],
            subtotal=subtotal,
        )
        total += subtotal

        movement = StockMovement.objects.create(
            movement_type=StockMovement.Type.OUT,
            warehouse_from=sale.warehouse,
            printer=item["printer"],
            qty=item["qty"],
            unit_price=item["price"],
            note=f"Sale #{sale.id}",
            created_by=user,
        )
        apply_movement(movement)

    sale.total = total
    sale.save(update_fields=["total"])
    return sale


@transaction.atomic
def create_return_with_items(*, return_data, items_data, user):
    ret = Return.objects.create(created_by=user, **return_data)

    for item in items_data:
        ReturnItem.objects.create(
            ret=ret,
            printer=item["printer"],
            qty=item["qty"],
            price=item["price"],
        )

        movement = StockMovement.objects.create(
            movement_type=StockMovement.Type.RETURN,
            warehouse_to=ret.warehouse,
            printer=item["printer"],
            qty=item["qty"],
            unit_price=item["price"],
            note=f"Return #{ret.id}",
            created_by=user,
        )
        apply_movement(movement)

    return ret
