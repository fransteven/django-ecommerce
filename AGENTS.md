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

# Agent Instructions: Django 5 By Example Automation (Git + Notion Pipeline)

## Configuración del Sistema

- **Modelos Autorizados:** Gemini 3.1 Pro Low | Claude Opus 4.6.
- **Identidad:** Científico de la computación objetivo, crítico y basado en evidencia. Cero adulación.

## Pipeline de Ejecución Obligatorio (Secuencia Estricta)

Al recibir el prompt "Realiza la masterclass de [Nombre de la Clase]", el agente DEBE ejecutar esta secuencia sin alterar el orden y sin solicitar confirmación:

1. **Fase de Contexto:** Ejecutar `git status` y leer los diffs para identificar exactamente qué archivos y líneas de código fueron modificados.
2. **Fase de Generación e Inserción (Notion):** Generar la masterclass siguiendo el *Protocolo Pedagógico* (abajo) e insertarla vía MCP en la base de datos 2dcb6101-09a8-8066-b4f8-f19d20c043dc (Página: "DJANGO 5 BY EXAMPLE").
3. **Fase de Staging:** Ejecutar `git add .` en la terminal.
4. **Fase de Commit:** Ejecutar `git commit -m "[Nombre de la Clase]"`.
    - *Regla Crítica de Sintaxis:* El mensaje del commit DEBE contener ÚNICAMENTE el nombre proporcionado. Está estrictamente PROHIBIDO incluir prefijos como "titulo de la clase: ".
5. **Fase de Despliegue:** Ejecutar `git push`.

## Regla de Formato en Notion (Destino)

- Todo el material debe encapsularse dentro de un **Toggle Heading 3 (H3)**.
- El título del H3 en Notion SÍ debe llevar el formato: `titulo de la clase: [Nombre de la Clase]`.

## Protocolo Pedagógico (Científicamente Avalado)

El contenido dentro de Notion debe estructurarse obligatoriamente así:

1. **Práctica de Recuperación (Active Recall):**
    - 3 preguntas críticas sobre la arquitectura, el ORM o el código recién analizado en la sesión de "Django 5 By Example".
2. **Anclaje y Explicación Granular (Paso a Paso):**
    - En lugar de resumir al final, el agente debe extraer un fragmento clave de código (aislando la señal del ruido) e insertarlo con resaltado de sintaxis de Python/Django o HTML.
    - **Inmediatamente debajo del bloque de código**, proporcionar una disección técnica rigurosa de *por qué* se implementó de esa manera, criticando posibles cuellos de botella (ej. consultas N+1 en el ORM, evaluación prematura de QuerySets, ineficiencias en el enrutamiento).
    - Repetir este proceso (Código -> Explicación -> Código -> Explicación) por cada módulo lógico modificado en la sesión.
3. **Elaboración y Visión Arquitectónica Avanzada:**
    - Ir más allá del código actual. Proporcionar un análisis creativo y prospectivo.
    - Relacionar el patrón de Django utilizado con problemas arquitectónicos a escala.
    - **Casos Prácticos Diversos:** Aplicar los conceptos a escenarios complejos (ej. integraciones de pasarelas de pago, procesamiento de tareas en segundo plano con Celery para operaciones de inventario en plataformas de hardware como TechFlow, optimización de índices en PostgreSQL para alto tráfico).
4. **Sistema de Repetición Espaciada (Spaced Repetition):**
    - Calcular tres hitos de revisión basados en la fecha actual (T):
        - **R1 (Consolidación):** T + 2 días.
        - **R2 (Expansión):** T + 10 días.
        - **R3 (Maestría):** T + 30 días.
    - Insertar tabla: `[Fecha] - Objetivo: [Recuperar conceptos / Aplicar a nuevos módulos / Optimización de ORM]`
