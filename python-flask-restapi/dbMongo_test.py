import pytest
from pymongo import MongoClient
from bson import ObjectId
from dbMongo import MongoDatabase  


@pytest.fixture(scope="module")
def mongo_client():
    client = MongoClient("mongodb://ekauffmann:123@localhost:5002/")
    yield client
    client.close()



@pytest.fixture(scope="module")
def mongo_database(mongo_client):
    database = MongoDatabase(mongo_client)
    yield database
    # Optionally, you may want to clean up the test data after testing
    # database.collection.delete_many({})



# Tests for MongoDatabase class
class TestMongoDatabase:
    def test_insert_encuesta(self, mongo_database):
        encuesta_data = {

            
            "id_encuesta": "1",
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
                    "Muy bueno"
                ]
                },
                {
                "texto_pregunta": "¿Recomendarías nuestro producto?",
                "tipo_pregunta": "eleccion_unica",
                "posibles_respuestas": ["Sí", "No"]
                }
            ]
            
        }

       # Add test data
        mongo_database.insert_encuesta(encuesta_data)
        assert len(mongo_database.get_encuestas()) == 1

    # Add similar test methods for other functions like get_encuestas, get_encuesta_by_id, etc.

    # Example of a test for update_encuesta
    def test_update_encuesta(self, mongo_database):
        encuesta_data = {}  # Add test data
        encuesta_id = ObjectId()  # Mock an ObjectId
        mongo_database.insert_encuesta(encuesta_data)
        updated_encuesta_data = {}  # Add updated test data
        mongo_database.update_encuesta(encuesta_id, updated_encuesta_data)
        assert mongo_database.get_encuesta_by_id(encuesta_id) == updated_encuesta_data

    # Add similar test methods for other update, delete, and retrieval functions


if __name__ == "__main__":
    pytest.main()