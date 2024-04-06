import redis

# Configurar la conexión a Redis
redis_client = redis.StrictRedis(
    host="localhost", port=6379, db=0, decode_responses=True
)


def get_data_from_database(data_id):
    # Aquí se realizaría la consulta a la base de datos para obtener los datos con el ID dado
    # Supongamos que los datos se almacenan en una variable llamada "data"
    data = {"id": data_id, "name": "Ejemplo"}
    return data


def get_data(data_id):
    # Intentar obtener los datos de la caché de Redis
    cached_data = redis_client.get(data_id)
    if cached_data:
        return cached_data
    else:
        # Si los datos no están en caché, obtenerlos de la base de datos y almacenarlos en caché
        data = get_data_from_database(data_id)
        redis_client.set(data_id, data)
        return data
