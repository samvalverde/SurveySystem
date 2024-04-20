import pytest
from unittest.mock import MagicMock
from surveyService import SurveyService
from mongomock import MongoClient

'''
client = MongoClient("mongo", 27017, username="root", password="password")
mongo_db = MongoDatabase(client)
'''

# Hay que instanciar MongoDatabase para llamar a los metodos reales


@pytest.fixture
def mock_mongo_collection():
    return MongoClient()['EncuestasDB']['encuestas']

@pytest.fixture
def survey_service(mock_mongo_collection):
    return SurveyService(mock_mongo_collection)

def test_insert_encuesta(survey_service, mock_mongo_collection):
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
    survey_service.insert_encuesta(encuesta_data)
    assert mock_mongo_collection.count_documents({}) == 1

def test_get_encuestas(survey_service, mock_mongo_collection):
    assert survey_service.get_encuestas() == []