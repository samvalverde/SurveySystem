import json
import pytest
from unittest.mock import MagicMock
from surveyService import SurveyService

@pytest.fixture
def mock_mongo_collection():
    return MagicMock()

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
    mock_mongo_collection.insert_one.assert_called_once_with(encuesta_data)

def test_get_encuestas(survey_service, mock_mongo_collection):
    survey_service.get_encuestas()
    mock_mongo_collection.find.assert_called_once_with({})