# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Perfil del Usuario

Soy un **Ingeniero de Sistemas recién graduado**. Hay muchos conceptos que desconozco, por lo que necesito explicaciones claras y detalladas cuando tengo dudas.

## Flujo de Aprendizaje con NotebookLM

Actualmente estoy aprendiendo Django con el libro **"Django 5 By Example" de Antonio Melé** (capítulo 9 en adelante).

- Libro completo en: `/Users/fransteven/Documents/LIBROS/FULLSTACK/Django 5 By Example, 5th Ed_ (2024) -- Antonio Melé.pdf`
- Notebook en NotebookLM: **"django by example 5"** (ID: `d960d5ec-b62a-4174-a77d-9e79e0bf560b`)

**Cuando el usuario tenga una duda sobre un tema:**
1. Explicar el concepto de forma clara y detallada (adaptada a un recién graduado)
2. Appendar la nueva nota al final de `notes.md` (ruta: `/Users/fransteven/Desktop/django-ecommerce/notes.md`)
3. Reemplazar la fuente en NotebookLM (borrar la anterior, subir el `notes.md` actualizado):
   ```bash
   # Borrar fuente anterior
   notebooklm source delete <source_id> --notebook d960d5ec-b62a-4174-a77d-9e79e0bf560b
   # Subir notes.md actualizado
   notebooklm source add /Users/fransteven/Desktop/django-ecommerce/notes.md --notebook d960d5ec-b62a-4174-a77d-9e79e0bf560b --json
   ```

**Nota:** El `source_id` actual de `notes.md` debe guardarse en memoria para poder borrarlo en la siguiente actualización.

## Setup

```bash
cd myshop/
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

RabbitMQ must be running on `localhost:5672` (default guest/guest credentials) for Celery tasks to work.

## Common Commands

```bash
# Django development
python manage.py runserver              # Start dev server
python manage.py makemigrations         # Create new migrations
python manage.py migrate                # Apply migrations
python manage.py shell                  # Interactive shell

# Run tests
python manage.py test                   # All tests
python manage.py test shop              # Single app

# Celery (run from myshop/ directory)
celery -A myshop worker -l info         # Start worker
celery -A myshop flower                 # Monitoring UI at :5555
```

> Note: the requirements file has a typo — it's `requiremets.txt`, not `requirements.txt`.

## Architecture

The project root is `myshop/` — all `manage.py` and `celery` commands must be run from there.

### Apps

**`shop/`** — Product catalog. `Category` and `Product` models with slug-based URLs. Product images are uploaded to `media/products/%Y/%m/%d/`.

**`cart/`** — Session-based shopping cart (no database model). The `Cart` class (`cart/cart.py`) stores items in Django sessions as `{product_id: {"quantity": int, "price": str}}`. A context processor (`cart/context_processors.py`) makes the cart available in all templates.

**`orders/`** — Order creation flow. `Order` and `OrderItem` models snapshot the price at order time. On successful order creation, `orders.tasks.order_created` is fired asynchronously via Celery to send an email confirmation.

### Celery

Configured in `myshop/celery.py` and initialized in `myshop/__init__.py`. The broker is RabbitMQ (`CELERY_BROKER_URL = "amqp://guest:guest@localhost:5672//"`). Currently one task: `orders.tasks.order_created`.

### Email

Using `django.core.mail.backends.console.EmailBackend` — emails print to the terminal, not sent.

### Templates

All templates live under `shop/templates/` (the shop app is used as the global template root):
- `shop/base.html` — base layout
- `shop/product/list.html`, `detail.html` — catalog pages
- `cart/detail.html` — cart page
- `orders/order/create.html`, `created.html` — checkout pages

### Media Files

`MEDIA_ROOT = BASE_DIR / "media"`, served at `/media/` in development via the URL configuration in `myshop/urls.py`.
