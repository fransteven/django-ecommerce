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

## 2. Filtros de base de datos en Django (`__lte` y `__gte`)

**Archivo:** `coupons/views.py` | **Capítulo:** 9+

### Contexto
En `coupons/views.py` vemos esta consulta a la base de datos (Django ORM):

```python
coupon = Coupon.objects.get(
    code__iexact=code,
    valid_from__lte=now,
    valid_to__gte=now,
    active=True,
)
```

Esta porción de código busca un registro en la tabla `Coupon` que cumpla con ciertas condiciones exactas. Aquí explicaremos qué significa cada parte, con un enfoque en `__lte` y campos de fecha.

### ¿Qué son los "Field Lookups" en Django?
En Django, cuando usamos métodos como `.get()` o `.filter()` para consultar la base de datos, podemos añadir sufijos a los nombres de los campos (separados por **doble guion bajo** `__`) para aplicar operadores lógicos como "mayor que", "menor que", "contiene", etc. A esto se le llama **Field Lookups**.

### Explicación de la lógica

1. **`code__iexact=code`**:
   - `code`: Es el campo de la base de datos donde se guarda el texto del cupón.
   - `__iexact`: Significa "exactamente igual, ignorando mayúsculas/minúsculas" (*case-insensitive exact match*). Entonces, si el código guardado es "VERANO10", coincidirá aunque el usuario escriba "verano10".

2. **`valid_from__lte=now`**:
   - `valid_from`: Es un campo tipo fecha/hora que indica "válido desde".
   - `__lte`: Viene del inglés **"Less Than or Equal to"**, que significa **"Menor o Igual que"** ($\le$).
   - Entonces, `valid_from__lte=now` le dice a la base de datos: *Asegúrate de que la fecha de inicio (`valid_from`) sea menor (que esté en el pasado) o igual al momento actual (`now`).* Es decir, verifica que el cupón "ya empezó a ser válido".

3. **`valid_to__gte=now`**:
   - `valid_to`: Es otra fecha que indica "válido hasta".
   - `__gte`: Viene de **"Greater Than or Equal to"**, que significa **"Mayor o Igual que"** ($\ge$).
   - `valid_to__gte=now` le dice a la base de datos: *Asegúrate de que la fecha de fin (`valid_to`) siga siendo mayor (en el futuro) o igual al momento actual.* Es decir, verifica que el cupón "todavía no ha caducado".

4. **`active=True`**:
   - Esto simplemente asegura que el administrador no haya puesto el cupón como "inactivo" manualmente desde el panel de administración.

### Resumen del uso de fechas
Al combinar `valid_from__lte=now` y `valid_to__gte=now`, Django está verificando que el "momento actual" (`now`) se encuentre justo en el rango de tiempo permitido para el cupón:

`valid_from`  $\le$  `now`  $\le$  `valid_to`

Si esta búsqueda tiene éxito, el método `.get()` te devuelve el objeto del cupón. Si no encuentra ninguno que cumpla estas cuatro condiciones simultáneamente, lanzará una excepción `Coupon.DoesNotExist`.
---

## 3. Recomendaciones con Redis (Sorted Sets)

**Archivo:** `shop/recomender.py` | **Capítulo:** 10

### Contexto
Para el sistema de recomendaciones, usamos **Redis**, una base de datos en memoria extremadamente rápida. En lugar de tablas relacionales, usamos una estructura llamada **Sorted Set** (Conjunto Ordenado).

### ¿Cómo funciona `r.zincrby`?

```python
r.zincrby(self.get_product_key(product_id), 1, with_id)
```

1. **El Key (`product:ID:purchased_with`)**: Cada producto tiene su propia "lista" en Redis que guarda qué otros productos se compraron con él.
2. **`zincrby` (Sorted Set Increment)**: 
   - Si el producto `with_id` ya existe en la lista del `product_id`, incrementa su puntuación en `1`.
   - Si no existe, lo añade con una puntuación inicial de `1`.
3. **Puntuación (Score)**: Cuantas más veces se compren juntos dos productos, mayor será su puntuación. Esto nos permite obtener fácilmente el "Top N" de productos recomendados pidiéndole a Redis los elementos con mayor puntuación.

### El flujo del código
El método `products_bought` recibe una lista de productos que se acaban de comprar.
- Hace un bucle doble para comparar cada producto con todos los demás de la compra.
- Si no son el mismo (`product_id != with_id`), registra en Redis que se compraron juntos.

---

## 4. Flujo Secuencial de `products_bought`

**Archivo:** `shop/recomender.py` | **Capítulo:** 10

### Contexto
Cuando un usuario completa una compra, necesitamos actualizar las sugerencias. Este método es el encargado de "entrenar" a nuestro motor de recomendaciones en Redis basado en los productos comprados juntos.

### Paso a Paso del Algoritmo

1.  **Entrada**: Recibe una lista de productos (`products`) que forman parte de una misma transacción.
2.  **Mapeo de IDs**: Se genera una lista `product_ids` con los IDs de cada producto. Esto facilita la comparación y el almacenamiento en Redis.
3.  **Bucle de Origen**: Se recorre cada producto de la lista (`product_id`). Este se trata como el "producto base".
4.  **Bucle de Destino**: Para cada producto base, se recorre **toda la lista** de nuevo (`with_id`).
5.  **Validación**: Se comprueba que `product_id != with_id`. Esto garantiza que no estemos recomendando un producto basándonos en que se compró consigo mismo.
6.  **Registro en Redis (`zincrby`)**:
    - **Clave**: Se genera una clave tipo `product:[id]:purchased_with`.
    - **Acción**: Se incrementa en **1** el valor del ID "compañero" (`with_id`).
    - **Resultado**: Redis guarda esto en un *Sorted Set*, ordenando automáticamente los productos por frecuencia de compra conjunta.

### ¿Por qué es eficiente?
Aunque es un bucle anidado ($O(N^2)$), las compras suelen tener pocos productos (menos de 10-20), por lo que la ejecución es instantánea. Redis maneja la ordenación en tiempo real, por lo que pedir las recomendaciones después es extremadamente rápido.

