# Notas de Aprendizaje — Django 5 by Example (Cap. 9+)

---

## 1. `reverse()` y `build_absolute_uri()` en conjunto

**Archivo:** `payment/views.py` | **Capítulo:** 9

### Contexto
En `payment/views.py` del proyecto myshop, estas dos funciones se usan para construir las URLs que Stripe necesita para redirigir al usuario tras el pago.

```python
success_url = request.build_absolute_uri(reverse("payment:completed"))
cancel_url  = request.build_absolute_uri(reverse("payment:canceled"))
```

### `reverse()` — Del nombre de URL a la ruta relativa

Django permite nombrar las URLs en `urls.py`:

```python
# payment/urls.py
path('completed/', views.payment_completed, name='completed'),
```

`reverse("payment:completed")` convierte ese nombre en la ruta relativa:

```
"payment:completed"  →  "/payment/completed/"
```

- `payment:` es el **namespace** del app (definido con `app_name` en urls.py)
- El `:` separa el namespace del nombre de la vista

**¿Por qué usar `reverse()` en vez de escribir la URL directamente?**
Si hardcodeas `/payment/completed/` y luego cambias la ruta en `urls.py`, el código se rompe. Con `reverse()` siempre apunta al lugar correcto automáticamente.

### `build_absolute_uri()` — De ruta relativa a URL completa

Stripe necesita una URL **completa** (con protocolo y dominio). Una ruta relativa no le sirve.

`request.build_absolute_uri(path)` usa el objeto `request` para construir la URL absoluta:

```
"/payment/completed/"  →  "http://127.0.0.1:8000/payment/completed/"
```

### Flujo completo

| Paso | Código | Resultado |
|------|--------|-----------|
| 1 | `reverse("payment:completed")` | `"/payment/completed/"` |
| 2 | `build_absolute_uri("/payment/completed/")` | `"http://127.0.0.1:8000/payment/completed/"` |
| 3 | Se pasa a Stripe como `success_url` | Stripe redirige aquí si el pago fue exitoso |

### Resumen
- `reverse()` → resuelve el nombre de una URL a su ruta relativa (evita hardcodear paths)
- `build_absolute_uri()` → convierte esa ruta relativa en una URL absoluta usando los datos del request actual
- Usados juntos son el patrón estándar en Django para generar URLs absolutas de forma segura y dinámica

---
