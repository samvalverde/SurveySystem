import pytest
from unittest.mock import MagicMock
from surveyService import SurveyService
from mongomock import MongoClient
from dbMongo import MongoDatabase  # Importa la clase MongoDatabase


@pytest.fixture
def mock_survey_service():
    return MagicMock()

@pytest.fixture
def mock_mongo_collection():
    return MongoClient()['EncuestasDB']['encuestas']

@pytest.fixture
def survey_service(mock_mongo_collection):
    return SurveyService(mock_mongo_collection)

# Hay que instanciar MongoDatabase para llamar a los metodos reales
mongoDb = MongoDatabase(mock_mongo_collection)

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

def test_convert_object_ids():
    from surveyService import SurveyService
    survey_service = SurveyService(None)  # Pass None because we don't need a database connection for this method
    data_with_object_id = {"_id": ObjectId("60bc8c4b04868f72f6f74abf"), "key": "value"}
    expected_data = {"_id": "60bc8c4b04868f72f6f74abf", "key": "value"}
    
    survey_service._convert_object_ids(data_with_object_id)
    
    assert data_with_object_id == expected_data

def test_add_question(mock_survey_service):
    from surveyService import SurveyService
    encuesta_id = "1"
    question_data = {
        "texto_pregunta": "¿Cuál es tu color favorito?",
        "tipo_pregunta": "abierta",
        "posibles_respuestas": []
    }
    mock_survey_service.collection.update_one.return_value.modified_count = 1
    
    result = mock_survey_service.add_question(encuesta_id, question_data)
    
    assert result is True
    mock_survey_service.collection.update_one.assert_called_once_with(
        {"id_encuesta": encuesta_id},
        {"$push": {"preguntas": question_data}}
    )

def test_update_question(mock_survey_service):
    from surveyService import SurveyService
    encuesta_id = "1"
    question_id = "1"
    updated_question_data = {
        "texto_pregunta": "¿Cuál es tu color favorito ahora?",
        "tipo_pregunta": "abierta",
        "posibles_respuestas": []
    }
    mock_survey_service.collection.update_one.return_value.modified_count = 1
    
    result = mock_survey_service.update_question(encuesta_id, question_id, updated_question_data)
    
    assert result is True
    mock_survey_service.collection.update_one.assert_called_once_with(
        {"id_encuesta": encuesta_id},
        {"$set": {"preguntas.0": updated_question_data}}
    )



