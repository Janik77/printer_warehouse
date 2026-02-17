from django.db import transaction
from django.db.models import F

from .models import StockBalance, StockMovement, Printer


@transaction.atomic
def apply_movement(mv: StockMovement) -> None:
    """
    Применяет движение к остаткам.
    Важное правило: остатки меняем ТОЛЬКО через движения.
    """
    qty = mv.qty

    # IN / RETURN -> добавляем на warehouse_to
    if mv.movement_type in [StockMovement.Type.IN, StockMovement.Type.RETURN]:
        if not mv.warehouse_to:
            raise ValueError("warehouse_to is required for IN/RETURN")

        bal, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_to, printer=mv.printer)
        StockBalance.objects.filter(pk=bal.pk).update(qty=F("qty") + qty)

    # OUT -> списываем с warehouse_from
    elif mv.movement_type == StockMovement.Type.OUT:
        if not mv.warehouse_from:
            raise ValueError("warehouse_from is required for OUT")

        bal, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_from, printer=mv.printer)
        StockBalance.objects.filter(pk=bal.pk).update(qty=F("qty") - qty)

    # TRANSFER -> минус со склада A, плюс на склад B
    elif mv.movement_type == StockMovement.Type.TRANSFER:
        if not mv.warehouse_from or not mv.warehouse_to:
            raise ValueError("warehouse_from and warehouse_to are required for TRANSFER")

        bal_from, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_from, printer=mv.printer)
        bal_to, _ = StockBalance.objects.get_or_create(warehouse=mv.warehouse_to, printer=mv.printer)
        StockBalance.objects.filter(pk=bal_from.pk).update(qty=F("qty") - qty)
        StockBalance.objects.filter(pk=bal_to.pk).update(qty=F("qty") + qty)

    # ADJUST -> пока не внедряем сложную логику, можно позже
    else:
        raise ValueError("Unsupported movement type")

    # Обновляем статус принтера грубо: если везде 0 — значит не на складе
    total_qty = StockBalance.objects.filter(printer=mv.printer).aggregate(models_sum=F("qty"))
