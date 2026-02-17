from django.db import transaction
from django.db.models import Sum

from .models import Printer, StockBalance, StockMovement


@transaction.atomic
def apply_movement(mv: StockMovement) -> None:
    """
    Apply stock movement to balances.
    Rule: balances are changed only through movements.
    """
    qty = mv.qty

    if mv.movement_type in [StockMovement.Type.IN, StockMovement.Type.RETURN]:
        if not mv.warehouse_to:
            raise ValueError("warehouse_to is required for IN/RETURN")

        bal, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_to, printer=mv.printer)
        bal.qty += qty
        bal.save(update_fields=["qty"])

    elif mv.movement_type == StockMovement.Type.OUT:
        if not mv.warehouse_from:
            raise ValueError("warehouse_from is required for OUT")

        bal, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_from, printer=mv.printer)
        bal.qty -= qty
        bal.save(update_fields=["qty"])

    elif mv.movement_type == StockMovement.Type.TRANSFER:
        if not mv.warehouse_from or not mv.warehouse_to:
            raise ValueError("warehouse_from and warehouse_to are required for TRANSFER")

        bal_from, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_from, printer=mv.printer)
        bal_to, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_to, printer=mv.printer)
        bal_from.qty -= qty
        bal_from.save(update_fields=["qty"])
        bal_to.qty += qty
        bal_to.save(update_fields=["qty"])
    else:
        raise ValueError("Unsupported movement type")

    total_qty = StockBalance.objects.filter(printer=mv.printer).aggregate(total=Sum("qty"))["total"] or 0
    mv.printer.status = Printer.Status.IN_STOCK if total_qty > 0 else Printer.Status.SOLD
    mv.printer.save(update_fields=["status"])
