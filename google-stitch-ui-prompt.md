# Google Stitch UI Prompt

## Objetivo

Generar una propuesta de UI para rediseñar solo estas vistas del ecommerce Django actual:

- listado de productos
- detalle de producto
- detalle del carrito
- crear orden / checkout
- orden creada

La propuesta debe ser visualmente moderna, clara y elegante, pero implementable sobre plantillas Django server-rendered sin cambiar la lógica de negocio.

## Mapeo real de templates

Base compartida:

- `myshop/shop/templates/shop/base.html`

Vistas incluidas en este rediseño:

- `myshop/shop/templates/shop/product/list.html`
- `myshop/shop/templates/shop/product/detail.html`
- `myshop/shop/templates/cart/detail.html`
- `myshop/shop/templates/orders/order/create.html`
- `myshop/shop/templates/orders/order/created.html`

Vistas excluidas del prompt:

- `myshop/shop/templates/orders/order/pdf.html`
- `myshop/shop/templates/admin/orders/order/detail.html`
- `myshop/shop/templates/payment/process.html`
- `myshop/shop/templates/payment/completed.html`
- `myshop/shop/templates/payment/canceled.html`

## Contexto funcional actual

El proyecto usa Django con renderizado del lado del servidor.

La plantilla base actual:

- muestra el logo `My shop`
- tiene un subheader con resumen del carrito
- renderiza el contenido principal dentro de un bloque `{% block content %}`

Las vistas usan datos reales ya expuestos por Django:

- producto: `name`, `price`, `image`, `description`, `category`
- categorías: lista completa y categoría activa
- carrito: productos, cantidad, precio unitario, subtotal por línea y total general
- checkout: formulario con `first_name`, `last_name`, `email`, `address`, `postal_code`, `city`
- orden creada: número de orden `order.id`

Restricciones importantes:

- no cambiar el flujo del ecommerce
- no depender de SPA
- no requerir JavaScript complejo
- no inventar nuevas pantallas
- no cambiar el backend ni los formularios
- debe poder implementarse con HTML/CSS sobre templates Django existentes

## Prompt para Google Stitch

```text
Diseña la UI de un ecommerce pequeño hecho con Django server-rendered. Quiero una propuesta visual completa, coherente y moderna con una dirección editorial limpia: minimalista, elegante, clara, con buena jerarquía visual, excelente uso del espacio en blanco, tipografía sobria, imágenes bien presentadas y una sensación de tienda curada. Evita el look genérico de dashboard SaaS o landing page de startup.

Importante:
- Solo diseña estas 5 vistas:
  1. Product listing
  2. Product detail
  3. Cart detail
  4. Checkout / create order
  5. Order created / success
- No agregues funcionalidades fuera de esas pantallas.
- La propuesta debe ser implementable sobre plantillas Django existentes y formularios HTML server-rendered.
- No dependas de SPA ni de JavaScript complejo.
- Conserva el flujo actual del ecommerce.

Contexto funcional de cada vista:

1. Product listing
- Pantalla principal del catálogo.
- Tiene un header global con logo y resumen del carrito.
- Tiene navegación por categorías.
- Debe mostrar:
  - título de la categoría activa o “Products”
  - lista de categorías con estado seleccionado
  - grid de productos
- Cada producto muestra:
  - imagen
  - nombre
  - precio
  - enlace al detalle
- Objetivo visual:
  - sidebar de categorías elegante e integrada
  - grid responsive
  - tarjetas limpias, premium y sobrias
  - tratamiento correcto para imágenes faltantes
  - hover states discretos

2. Product detail
- Pantalla de detalle individual.
- Debe mostrar:
  - imagen principal
  - nombre
  - categoría con enlace
  - precio
  - descripción
  - formulario simple para agregar al carrito
- El formulario actual contiene selector de cantidad y botón “Add to cart”.
- Objetivo visual:
  - foco en la imagen y el precio
  - CTA principal visible
  - lectura cómoda de la descripción
  - apariencia premium en desktop y mobile

3. Cart detail
- Pantalla de detalle del carrito.
- Debe mostrar:
  - imagen del producto
  - nombre
  - cantidad editable
  - acción de eliminar
  - precio unitario
  - subtotal por producto
  - total general
- También incluye:
  - botón “Continue shopping”
  - botón “Checkout”
- Objetivo visual:
  - reinterpretar la tabla básica de forma más moderna
  - mantener claridad total en precios y cantidades
  - total y CTA de checkout muy destacados
  - excelente adaptación móvil

4. Checkout / create order
- Pantalla de checkout.
- Tiene dos bloques principales:
  - resumen del pedido
  - formulario de datos del cliente
- El resumen del pedido contiene:
  - lista de productos
  - cantidad por producto
  - subtotal por línea
  - total general
- El formulario contiene exactamente estos campos:
  - first_name
  - last_name
  - email
  - address
  - postal_code
  - city
- Objetivo visual:
  - diseño limpio, confiable y fácil de completar
  - formulario muy legible
  - resumen del pedido separado visualmente
  - CTA principal “Place order”

5. Order created / success
- Pantalla final de confirmación.
- Debe mostrar:
  - mensaje de agradecimiento
  - confirmación de éxito
  - número de orden
- Objetivo visual:
  - sensación de cierre correcta
  - diseño simple, limpio y memorable
  - destacar el número de orden

Dirección visual:
- estilo editorial limpio
- paleta neutra con uno o dos colores de acento
- tipografía con personalidad pero fácil de traducir a web
- bordes, sombras y profundidad sutiles
- componentes sobrios y refinados
- imágenes de producto con protagonismo
- excelente responsive design

Entregables:
- una propuesta visual consistente para las 5 pantallas
- componentes reutilizables compartidos entre vistas
- estados desktop y mobile
- diseño suficientemente específico para traducirse luego a HTML/CSS en Django templates
```

## Uso esperado

1. Copiar el bloque `Prompt para Google Stitch`.
2. Generar la propuesta visual en Stitch.
3. Usar esa propuesta como base para rediseñar:
   - `shop/base.html`
   - `shop/product/list.html`
   - `shop/product/detail.html`
   - `cart/detail.html`
   - `orders/order/create.html`
   - `orders/order/created.html`
4. Ajustar estilos en `myshop/shop/static/css/base.css` o dividirlos en archivos más específicos si conviene.
