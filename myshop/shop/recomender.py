import redis
from django.conf import settings

# connect to redis
r = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)


class Recommender:
    # Genera la clave (string) única en Redis para la "lista" de un producto específico
    def get_product_key(self, id):
        return f"product:{id}:purchased_with"

    # Método que recibe los productos de una orden para registrar que se compraron juntos
    def products_bought(self, products):
        # Extrae solo los IDs de la lista de objetos 'products' (ej: [1, 3, 4])
        product_ids = [p.id for p in products]

        # Bucle 1: Selecciona un producto de la lista para usarlo como "base"
        for product_id in product_ids:
            # Bucle 2: Lo combina con todos los demás productos de esa misma lista
            for with_id in product_ids:
                # Condición: Evita relacionar un producto consigo mismo (ej: ID 1 con ID 1)
                if product_id != with_id:
                    # R.ZINCRBY (Redis Sorted Set Increment By):
                    # Va a la clave del producto base (self.get_product_key)
                    # e incrementa en 1 la puntuación (score) del producto compañero (with_id).
                    # Si el producto compañero no existía en la lista, lo crea con score 1.
                    # Parametros de zincrby(key,increment,member)
                    r.zincrby(self.get_product_key(product_id), 1, with_id)
