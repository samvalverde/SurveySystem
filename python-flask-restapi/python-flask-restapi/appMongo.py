from pymongo import MongoClient

# Establecer la conexión con MongoDB
client = MongoClient("localhost", 27017, username="root", password="example")
db = client[
    "EncuestasDB"
]  # Reemplaza "mi_base_de_datos" con el nombre de tu base de datos
encuestas_collection = db["encuestas"]

# Datos de ejemplo para una encuesta
encuesta_data = {
    "id_encuesta": 1,
    "titulo_encuesta": "Encuesta de satisfacción",
    "preguntas": [
        {
            "texto_pregunta": "¿Cómo calificarías nuestro servicio?",
            "tipo_pregunta": "escala_calificacion",
            "posibles_respuestas": [
                "Muy malo",
                "Malo",
                "Regular",
                "Bueno",
                "Muy bueno",
            ],
        },
        {
            "texto_pregunta": "¿Recomendarías nuestro producto?",
            "tipo_pregunta": "eleccion_unica",
            "posibles_respuestas": ["Sí", "No"],
        },
    ],
}

# Insertar la encuesta en la colección "encuestas"
encuestas_collection.insert_one(encuesta_data)

print("Encuesta insertada correctamente.")
