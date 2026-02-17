# Printer Warehouse

Django + DRF проект для учета складов, принтеров, движений, продаж и возвратов.

## Запуск

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install django djangorestframework
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Web UI (Django Templates)

UI доступен только для авторизованных пользователей.

- Логин: `http://127.0.0.1:8000/login/`
- Dashboard: `http://127.0.0.1:8000/`
- Warehouses CRUD: `http://127.0.0.1:8000/warehouses/`
- Printers CRUD + filters: `http://127.0.0.1:8000/printers/`
- Movements list/create: `http://127.0.0.1:8000/movements/`
- Sales list/create: `http://127.0.0.1:8000/sales/`
- Returns list/create: `http://127.0.0.1:8000/returns/`
- Django Admin: `http://127.0.0.1:8000/admin/`

## API

API доступно по префиксу: `http://127.0.0.1:8000/api/`

Для всех `/api/` endpoint требуется авторизация (минимальные permissions: только залогиненные пользователи).

Пример Basic Auth:

```bash
curl -u admin:admin http://127.0.0.1:8000/api/warehouses/
```

### Endpoint'ы

- `GET/POST /api/warehouses/`
- `GET/POST /api/printers/`
- `GET/POST /api/movements/`
- `GET/POST /api/customers/`
- `GET/POST /api/sales/`
- `GET/POST /api/sale-items/`
- `GET/POST /api/returns/`
- `GET/POST /api/return-items/`

### Фильтры

#### Printers

- `serial` — поиск по части серийного номера
- `status` — фильтр по статусу
- `warehouse` — `id` склада

Пример:

```bash
curl -u admin:admin "http://127.0.0.1:8000/api/printers/?serial=SN&status=IN_STOCK&warehouse=1"
```

#### Movements

- `date_from` — дата начала (по `created_at`)
- `date_to` — дата окончания (по `created_at`)
- `type` — тип движения (`IN`, `OUT`, `TRANSFER`, `RETURN`, `ADJUST`)
- `warehouse` — `id` склада (ищет и в `warehouse_from`, и в `warehouse_to`)

Пример:

```bash
curl -u admin:admin "http://127.0.0.1:8000/api/movements/?date_from=2026-01-01&date_to=2026-12-31&type=TRANSFER&warehouse=1"
```

#### Sales

- `customer` — `id` клиента
- `warehouse` — `id` склада
- `date_from` — дата начала продажи (по `sale_date`)
- `date_to` — дата окончания продажи (по `sale_date`)

Пример:

```bash
curl -u admin:admin "http://127.0.0.1:8000/api/sales/?customer=1&warehouse=2&date_from=2026-01-01&date_to=2026-12-31"
```
