import sys
import os

# Agrega la ruta al directorio que contiene db.py al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import MagicMock, patch
from db import Database
from dbMongo import MongoDatabase

# ---------------------------------------------------------------- Fixture para la base de datos de PostgreSQL ----------------------------------------------------------------
@pytest.fixture
def db():
    # Mockear la conexión de la base de datos
    conn_mock = MagicMock()
    return Database(conn_mock)


def test_login_user(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    cursor_mock.fetchall.return_value = [("user1", "password1", "role1")]
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    result = db.login_user("user1", "password1")

    # Verificar que se llamó al método execute y que devolvió el resultado esperado
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        "SELECT * FROM Usuario WHERE Username = 'user1' AND Password = 'password1';"
    )
    assert result == [("user1", "password1", "role1")]


# Test fallido para test_login_user
def test_login_user_failure(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    cursor_mock.fetchall.return_value = []  # Simular que no se encontró el usuario
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    result = db.login_user("user1", "password1")

    # Verificar que se llamó al método execute y que devolvió el resultado esperado
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        "SELECT * FROM Usuario WHERE Username = 'user1' AND Password = 'password1';"
    )
    assert result == []  # El resultado debería ser una lista vacía


def test_get_users(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    cursor_mock.fetchall.return_value = [("user1", "password1", "role1")]
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    users = db.get_users()

    # Verificar que se llamó al método execute y que devolvió el resultado esperado
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with("SELECT * FROM Usuario;")
    assert users == [("user1", "password1", "role1")]


# Test fallido para test_get_users
def test_get_users_failure(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    cursor_mock.fetchall.return_value = []  # Simular que no se encontraron usuarios
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    users = db.get_users()

    # Verificar que se llamó al método execute y que devolvió el resultado esperado
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with("SELECT * FROM Usuario;")
    assert users == []  # La lista de usuarios debería estar vacía


def test_create_user(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    db.conn.cursor.return_value = cursor_mock

    # Datos de usuario de ejemplo
    user_data = {
        "Nombre": "John Doe",
        "Username": "johndoe",
        "Password": "123456",
        "IdTipoRole": "user",
    }

    # Probar el método
    created_user = db.create_user(user_data)

    # Verificar que se llamó al método execute y que se commitió la transacción
    db.conn.cursor.assert_called_once()
    expected_sql = f"INSERT INTO Usuario (Nombre, Username, Password, IdTipoRole) VALUES ('{user_data['Nombre']}', '{user_data['Username']}', '{user_data['Password']}', '{user_data['IdTipoRole']}');"
    actual_sql = cursor_mock.execute.call_args[0][
        0
    ]  # Obtener la primera llamada al método execute y su primer argumento
    assert expected_sql.replace(" ", "") == actual_sql.replace(
        " ", ""
    ), f"Expected: {expected_sql}\nActual: {actual_sql}"
    db.conn.commit.assert_called_once()

    # Verificar que el usuario creado coincide con los datos proporcionados
    assert created_user == user_data


# Test fallido para test_create_user
def test_create_user_failure(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    db.conn.cursor.return_value = cursor_mock

    # Datos de usuario de ejemplo
    user_data = {
        "Nombre": "John Doe",
        "Username": "johndoe",
        "Password": "123456",
        "IdTipoRole": "user",
    }

    # Probar el método
    created_user = db.create_user(user_data)

    # Verificar que se llamó al método execute y que se commitió la transacción
    db.conn.cursor.assert_called_once()
    expected_sql = f"INSERT INTO Usuario (Nombre, Username, Password, IdTipoRole) VALUES ('{user_data['Nombre']}', '{user_data['Username']}', '{user_data['Password']}', '{user_data['IdTipoRole']}');"
    actual_sql = cursor_mock.execute.call_args[0][
        0
    ]  # Obtener la primera llamada al método execute y su primer argumento
    assert expected_sql.replace(" ", "") == actual_sql.replace(
        " ", ""
    ), f"Expected: {expected_sql}\nActual: {actual_sql}"
    db.conn.commit.assert_called_once()

    # Verificar que el usuario creado coincide con los datos proporcionados
    assert created_user == user_data


def test_get_User_by_ID(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    cursor_mock.fetchall.return_value = [("user1", "password1", "role1")]
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    user_id = 1
    user = db.get_User_by_ID(user_id)

    # Verificar que se llamó al método execute con el ID del usuario y que devolvió el resultado esperado
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        f"SELECT * FROM Usuario WHERE Id = {user_id};"
    )
    assert user == [("user1", "password1", "role1")]


# Test fallido para test_get_User_by_ID
def test_get_User_by_ID_failure(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    cursor_mock.fetchall.return_value = []  # Simular que no se encontró el usuario
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    user_id = 1
    user = db.get_User_by_ID(user_id)

    # Verificar que se llamó al método execute con el ID del usuario y que devolvió el resultado esperado
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        f"SELECT * FROM Usuario WHERE Id = {user_id};"
    )
    assert user == []  # El resultado debería ser una lista vacía


def test_update_user(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    db.conn.cursor.return_value = cursor_mock

    # Datos de usuario actualizados
    updated_user_data = {
        "Nombre": "Updated User",
        "Username": "updateduser",
        "Password": "updatedpassword",
        "IdTipoRole": "admin",
    }

    # Probar el método
    user_id = 1
    updated_user = db.update_user(updated_user_data, user_id)

    # Verificar que se llamó al método execute con los datos actualizados y que se commitió la transacción
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        f"UPDATE Usuario SET Nombre = '{updated_user_data['Nombre']}', Username = '{updated_user_data['Username']}', Password = '{updated_user_data['Password']}', IdTipoRole = '{updated_user_data['IdTipoRole']}' WHERE Id = {user_id};"
    )
    db.conn.commit.assert_called_once()

    # Verificar que el usuario actualizado coincide con los datos proporcionados
    assert updated_user == updated_user_data


# Test fallido para test_update_user
def test_update_user_failure(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    db.conn.cursor.return_value = cursor_mock

    # Datos de usuario actualizados
    updated_user_data = {
        "Nombre": "Updated User",
        "Username": "updateduser",
        "Password": "updatedpassword",
        "IdTipoRole": "admin",
    }

    # Probar el método
    user_id = 1
    updated_user = db.update_user(updated_user_data, user_id)

    # Verificar que se llamó al método execute con los datos actualizados y que se commitió la transacción
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        f"UPDATE Usuario SET Nombre = '{updated_user_data['Nombre']}', Username = '{updated_user_data['Username']}', Password = '{updated_user_data['Password']}', IdTipoRole = '{updated_user_data['IdTipoRole']}' WHERE Id = {user_id};"
    )
    db.conn.commit.assert_called_once()

    # Verificar que el usuario actualizado coincide con los datos proporcionados
    assert updated_user == updated_user_data


def test_delete_user(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    user_id = 1
    deleted_user_id = db.delete_user(user_id)

    # Verificar que se llamó al método execute con el ID del usuario y que se commitió la transacción
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        f"DELETE FROM Usuario WHERE Id = {user_id};"
    )
    db.conn.commit.assert_called_once()

    # Verificar que el ID del usuario eliminado coincide con el proporcionado
    assert deleted_user_id == user_id


# Test fallido para test_delete_user
def test_delete_user_failure(db):
    # Mockear el cursor y su ejecución
    cursor_mock = MagicMock()
    db.conn.cursor.return_value = cursor_mock

    # Probar el método
    user_id = 1
    deleted_user_id = db.delete_user(user_id)

    # Verificar que se llamó al método execute con el ID del usuario y que se commitió la transacción
    db.conn.cursor.assert_called_once()
    cursor_mock.execute.assert_called_once_with(
        f"DELETE FROM Usuario WHERE Id = {user_id};"
    )
    db.conn.commit.assert_called_once()

    # Verificar que el ID del usuario eliminado coincide con el proporcionado
    assert deleted_user_id == user_id


# ---------------------------------------------------------------- Fixture para la base de datos de MongoDB ----------------------------------------------------------------


@pytest.fixture
def mongo_db():
    # Mockear el cliente MongoDB
    mongo_client_mock = MagicMock()
    mongo_db = MongoDatabase(mongo_client_mock)
    mock_collection = MagicMock()
    mock_result = MagicMock()
    mock_result.modified_count = 1
    mock_collection.update_one.return_value = mock_result
    return mongo_db

    # ------------------------------------------------------- SECCION DE ENCUESTAS -------------------------------------------------------


# Prueba para el método insert_encuesta
def test_insert_encuesta(mongo_db):
    # Mockear la colección de encuestas
    mongo_db.collection = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_data = {
        "id_encuesta": "1",
        "titulo_encuesta": "Encuesta de prueba",
        "publica": True,
        "preguntas": [],
    }

    # Probar el método
    mongo_db.insert_encuesta(encuesta_data)

    # Verificar que se llamó al método insert_one de la colección de encuestas
    mongo_db.collection.insert_one.assert_called_once_with(encuesta_data)


# Prueba para el método insert_encuesta con fallo
def test_insert_encuesta_failure(mongo_db):
    # Mockear la colección de encuestas
    mongo_db.collection = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_data = {
        "id_encuesta": "1",
        "titulo_encuesta": "Encuesta de prueba",
        "publica": True,
        "preguntas": [],
    }

    # Lanzar un error al llamar al método insert_one de la colección de encuestas
    mongo_db.collection.insert_one.side_effect = Exception("Error al insertar encuesta")

    # Probar el método
    with pytest.raises(Exception):
        mongo_db.insert_encuesta(encuesta_data)


# Prueba para el método get_encuestas
def test_get_encuestas(mongo_db):
    # Mockear la colección de encuestas
    mongo_db.collection = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_data = {
        "id_encuesta": "1",
        "titulo_encuesta": "Encuesta de prueba",
        "publica": "True",
        "preguntas": [],
    }

    # Mockear el retorno de la colección de encuestas
    mongo_db.collection.find.return_value = [encuesta_data]

    # Probar el método
    encuestas = mongo_db.get_encuestas()

    # Verificar que se obtuvieron las encuestas correctamente
    assert len(encuestas) == 1
    assert encuestas[0]["id_encuesta"] == "1" and encuestas[0]["publica"] == "True"


# Prueba para el método get_encuestas con fallo
def test_get_encuestas_failure(mongo_db):
    # Mockear la colección de encuestas
    mongo_db.collection = MagicMock()

    # Lanzar un error al llamar al método find de la colección de encuestas
    mongo_db.collection.find.side_effect = Exception("Error al obtener encuestas")

    # Probar el método
    with pytest.raises(Exception):
        mongo_db.get_encuestas()


# Prueba para el método get_encuesta_by_id
def test_get_encuesta_by_id(mongo_db):
    # Mockear la colección de encuestas
    mongo_db.collection = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_data = {
        "id_encuesta": "1",
        "titulo_encuesta": "Encuesta de prueba",
        "publica": True,
        "preguntas": [],
    }

    # Mockear el retorno de la colección de encuestas
    mongo_db.collection.find_one.return_value = encuesta_data

    # Probar el método
    encuesta = mongo_db.get_encuesta_by_id("1")

    # Verificar que se obtuvo la encuesta correctamente
    assert encuesta["id_encuesta"] == "1"


# Prueba para el método get_encuesta_by_id con fallo
def test_get_encuesta_by_id_failure(mongo_db):
    # Mockear la colección de encuestas
    mongo_db.collection = MagicMock()

    # Lanzar un error al llamar al método find_one de la colección de encuestas
    mongo_db.collection.find_one.side_effect = Exception(
        "Error al obtener encuesta por ID"
    )

    # Probar el método
    with pytest.raises(Exception):
        mongo_db.get_encuesta_by_id("1")


# Prueba para el método update_encuesta
def test_update_encuesta(mongo_db):
    # Mockear el retorno del método update_one
    mongo_db.collection.update_one.return_value.modified_count = 1

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    updated_encuesta_data = {
        "titulo_encuesta": "Encuesta actualizada",
        "publica": True,
        "preguntas": [],
    }

    # Probar el método
    result = mongo_db.update_encuesta(encuesta_id, updated_encuesta_data)

    # Verificar que se actualizó la encuesta correctamente
    assert result == updated_encuesta_data


# Prueba para el método update_encuesta con fallo
def test_update_encuesta_failure(mongo_db):
    # Mockear el retorno del método update_one
    mongo_db.collection.update_one.return_value.modified_count = (
        0  # Simular fallo en la actualización
    )

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    updated_encuesta_data = {
        "titulo_encuesta": "Encuesta actualizada",
        "publica": True,
        "preguntas": [],
    }

    # Probar el método
    result = mongo_db.update_encuesta(encuesta_id, updated_encuesta_data)

    # Verificar que la actualización falló
    assert result == None


# Prueba para el método delete_encuesta
def test_delete_encuesta(mongo_db):
    # Mockear el retorno del método delete_one
    mongo_db.collection.delete_one.return_value.deleted_count = 1

    # Datos de encuesta de ejemplo
    encuesta_id = "1"

    # Probar el método
    result = mongo_db.delete_encuesta(encuesta_id)

    # Verificar que se eliminó la encuesta correctamente
    assert result == 1


# Prueba para el método delete_encuesta con fallo
def test_delete_encuesta_failure(mongo_db):
    # Mockear el retorno del método delete_one
    mongo_db.collection.delete_one.return_value.deleted_count = (
        0  # Simular fallo en la eliminación
    )

    # Datos de encuesta de ejemplo
    encuesta_id = "1"

    # Probar el método
    result = mongo_db.delete_encuesta(encuesta_id)

    # Verificar que la eliminación falló
    assert result == 0


# Prueba para el método publish_encuesta
def test_publish_encuesta(mongo_db):
    # Mockear el método update_encuesta_key
    mongo_db.update_encuesta_key = MagicMock(return_value=True)

    # Datos de encuesta de ejemplo
    encuesta_id = "1"

    # Probar el método
    result = mongo_db.publish_encuesta(encuesta_id)

    # Verificar que la publicación fue exitosa
    assert result == True


# Prueba para el método publish_encuesta con fallo
def test_publish_encuesta_failure(mongo_db):
    # Mockear el método update_encuesta_key para simular un fallo
    mongo_db.update_encuesta_key = MagicMock(return_value=False)

    # Datos de encuesta de ejemplo
    encuesta_id = "1"

    # Probar el método
    result = mongo_db.publish_encuesta(encuesta_id)

    # Verificar que la publicación falló
    assert result == False
    # ------------------------------------------------------- SECCION DE PREGUNTAS -------------------------------------------------------


# Prueba para el método add_question
def test_add_question(mongo_db):
    # Mockear el retorno del método update_one
    mongo_db.collection.update_one.return_value.modified_count = 1

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    question_data = {
        "posibles_respuestas": ["Opción 1", "Opción 2"],
        "texto_pregunta": "Pregunta nueva",
        "tipo_pregunta": "eleccion_unica",
    }

    # Probar el método
    result = mongo_db.add_question(encuesta_id, question_data)

    # Verificar que se agregó la pregunta correctamente
    assert result == True


# Prueba para el método add_question con fallo
def test_add_question_failure(mongo_db):
    # Mockear el retorno del método update_one
    mongo_db.collection.update_one.return_value.modified_count = (
        0  # Simular fallo en la actualización
    )

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    question_data = {
        "posibles_respuestas": ["Opción 1", "Opción 2"],
        "texto_pregunta": "Pregunta nueva",
        "tipo_pregunta": "eleccion_unica",
    }

    # Probar el método
    result = mongo_db.add_question(encuesta_id, question_data)

    # Verificar que la adición de la pregunta falló
    assert result == False


# Prueba para el método get_questions
def test_get_questions(mongo_db):
    # Mockear el retorno del método get_encuesta_by_id
    mongo_db.get_encuesta_by_id = MagicMock(
        return_value={"preguntas": ["Pregunta 1", "Pregunta 2"]}
    )

    # Datos de encuesta de ejemplo
    encuesta_id = "1"

    # Probar el método
    questions = mongo_db.get_questions(encuesta_id)

    # Verificar que se obtuvieron las preguntas correctamente
    assert len(questions) == 2
    assert questions[0] == "Pregunta 1"


# Prueba para el método get_questions con fallo
def test_get_questions_failure(mongo_db):
    # Mockear el retorno del método get_encuesta_by_id para simular un fallo
    mongo_db.get_encuesta_by_id = MagicMock(return_value=None)

    # Datos de encuesta de ejemplo
    encuesta_id = "1"

    # Probar el método
    questions = mongo_db.get_questions(encuesta_id)

    # Verificar que la obtención de preguntas falló
    assert questions == []


# Prueba para el método update_question
def test_update_question(mongo_db):
    # Mockear el retorno del método update_one
    mongo_db.collection.update_one.return_value.modified_count = 1

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    question_id = "1"
    updated_question_data = {
        "posibles_respuestas": ["Opción 1", "Opción 2"],
        "texto_pregunta": "Pregunta actualizada",
        "tipo_pregunta": "eleccion_unica",
    }

    # Probar el método
    result = mongo_db.update_question(encuesta_id, question_id, updated_question_data)

    # Verificar que se actualizó la pregunta correctamente
    assert result == True


# Prueba para el método update_question con fallo
def test_update_question_failure(mongo_db):
    # Mockear el retorno del método update_one
    mongo_db.collection.update_one.return_value.modified_count = (
        0  # Simular fallo en la actualización
    )

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    question_id = "1"
    updated_question_data = {
        "posibles_respuestas": ["Opción 1", "Opción 2"],
        "texto_pregunta": "Pregunta actualizada",
        "tipo_pregunta": "eleccion_unica",
    }

    # Probar el método
    result = mongo_db.update_question(encuesta_id, question_id, updated_question_data)

    # Verificar que la actualización de la pregunta falló
    assert result == False


# ------------------------------------------------------- SECCION DE RESPUESTAS A ENCUESTAS -------------------------------------------------------


# Prueba para el método submit_response
def test_submit_response(mongo_db):
    # Mockear la colección de respuestas
    mongo_db.responsesCollect = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    usuario_id = "123"
    response_data = [
        {"texto_pregunta": "Pregunta 1", "respuesta": "Respuesta 1"},
        {"texto_pregunta": "Pregunta 2", "respuesta": "Respuesta 2"},
    ]

    # Mockear el retorno de la inserción de la colección de respuestas
    mongo_db.responsesCollect.insert_one.return_value = True

    # Probar el método
    result = mongo_db.submit_response(encuesta_id, usuario_id, response_data)

    # Verificar que la inserción fue exitosa
    assert result == True


# Prueba para el método submit_response
def test_submit_response_failure(mongo_db):
    # Mockear la colección de respuestas
    mongo_db.responsesCollect = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    usuario_id = "123"
    response_data = [
        {"texto_pregunta": "Pregunta 1", "respuesta": "Respuesta 1"},
        {"texto_pregunta": "Pregunta 2", "respuesta": "Respuesta 2"},
    ]

    # Mockear el retorno de la inserción de la colección de respuestas
    mongo_db.responsesCollect.insert_one.return_value = False

    # Probar el método
    result = mongo_db.submit_response(encuesta_id, usuario_id, response_data)

    # Verificar que la inserción falló
    assert result == False


# Prueba para el método get_responses
def test_get_responses(mongo_db):
    # Mockear la colección de respuestas
    mongo_db.responsesCollect = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    response_data = [
        {
            "usuario_id": "123",
            "respuestas": [
                {"texto_pregunta": "Pregunta 1", "respuesta": "Respuesta 1"},
                {"texto_pregunta": "Pregunta 2", "respuesta": "Respuesta 2"},
            ],
        },
        {
            "usuario_id": "456",
            "respuestas": [
                {"texto_pregunta": "Pregunta 1", "respuesta": "Respuesta 3"},
                {"texto_pregunta": "Pregunta 2", "respuesta": "Respuesta 4"},
            ],
        },
    ]

    # Mockear el retorno de la colección de respuestas
    mongo_db.responsesCollect.find.return_value = response_data

    # Probar el método
    responses = mongo_db.get_responses(encuesta_id)

    # Verificar que se obtuvieron las respuestas correctamente
    assert len(responses) == 4
    assert responses[0]["texto_pregunta"] == "Pregunta 1"
    assert responses[1]["respuesta"] == "Respuesta 2"

    # -------------------------------------------------------------- ANALISIS DE RESPUESTAS --------------------------------------------------------------


def test_generate_analysis(mongo_db):
    # Mockear la colección de respuestas
    mongo_db.responsesCollect = MagicMock()

    # Datos de encuesta de ejemplo
    encuesta_id = "1"
    response_data = [
        {
            "usuario_id": "123",
            "respuestas": [
                {"texto_pregunta": "Pregunta 1", "respuesta": "Respuesta 1"},
                {"texto_pregunta": "Pregunta 2", "respuesta": "Respuesta 2"},
            ],
        },
        {
            "usuario_id": "456",
            "respuestas": [
                {"texto_pregunta": "Pregunta 1", "respuesta": "Respuesta 3"},
                {"texto_pregunta": "Pregunta 2", "respuesta": "Respuesta 4"},
            ],
        },
    ]

    # Mockear el retorno de la colección de respuestas
    mongo_db.responsesCollect.find.return_value = response_data

    # Probar el método
    success, analysis = mongo_db.generate_analysis(encuesta_id)

    # Verificar que se generó el análisis correctamente
    assert success == True
    assert len(analysis) == 2
    assert analysis["Pregunta 1"]["Respuesta 1"] == 1
    assert analysis["Pregunta 2"]["Respuesta 4"] == 1


# ------------------------------------------------------- SECCION DE EDICION DE ENCUESTAS COLABORATIVAS ------------------------------------------------------


def test_start_edit_session():
    # Simular una instancia del objeto que contiene el método start_edit_session
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock
    edit_manager.start_edit_session.return_value = True

    # Llamar al método start_edit_session con un identificador de encuesta
    result = edit_manager.start_edit_session("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == True
    # Verificar que se llamó al método start_edit_session con el argumento esperado
    edit_manager.start_edit_session.assert_called_once_with("encuesta_id")


def test_save_edit_changes():
    # Simular una instancia del objeto que contiene el método save_edit_changes
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock
    edit_manager.save_edit_changes.return_value = True

    # Llamar al método save_edit_changes con un identificador de encuesta
    result = edit_manager.save_edit_changes("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == True
    # Verificar que se llamó al método save_edit_changes con el argumento esperado
    edit_manager.save_edit_changes.assert_called_once_with("encuesta_id")


def test_submit_edit_changes():
    # Simular una instancia del objeto que contiene el método submit_edit_changes
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock
    edit_manager.submit_edit_changes.return_value = True

    # Llamar al método submit_edit_changes con un identificador de encuesta
    result = edit_manager.submit_edit_changes("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == True
    # Verificar que se llamó al método submit_edit_changes con el argumento esperado
    edit_manager.submit_edit_changes.assert_called_once_with("encuesta_id")


def test_get_edit_session_status():
    # Simular una instancia del objeto que contiene el método get_edit_session_status
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock
    edit_manager.get_edit_session_status.return_value = "Últimos cambios aplicados"

    # Llamar al método get_edit_session_status con un identificador de encuesta
    result = edit_manager.get_edit_session_status("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == "Últimos cambios aplicados"
    # Verificar que se llamó al método get_edit_session_status con el argumento esperado
    edit_manager.get_edit_session_status.assert_called_once_with("encuesta_id")


def test_start_edit_session_failure():
    # Simular una instancia del objeto que contiene el método start_edit_session
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock para que el método falle
    edit_manager.start_edit_session.return_value = False

    # Llamar al método start_edit_session con un identificador de encuesta
    result = edit_manager.start_edit_session("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == False
    # Verificar que se llamó al método start_edit_session con el argumento esperado
    edit_manager.start_edit_session.assert_called_once_with("encuesta_id")


def test_save_edit_changes_failure():
    # Simular una instancia del objeto que contiene el método save_edit_changes
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock para que el método falle
    edit_manager.save_edit_changes.return_value = False

    # Llamar al método save_edit_changes con un identificador de encuesta
    result = edit_manager.save_edit_changes("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == False
    # Verificar que se llamó al método save_edit_changes con el argumento esperado
    edit_manager.save_edit_changes.assert_called_once_with("encuesta_id")


def test_submit_edit_changes_failure():
    # Simular una instancia del objeto que contiene el método submit_edit_changes
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock para que el método falle
    edit_manager.submit_edit_changes.return_value = False

    # Llamar al método submit_edit_changes con un identificador de encuesta
    result = edit_manager.submit_edit_changes("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == False
    # Verificar que se llamó al método submit_edit_changes con el argumento esperado
    edit_manager.submit_edit_changes.assert_called_once_with("encuesta_id")


def test_get_edit_session_status_failure():
    # Simular una instancia del objeto que contiene el método get_edit_session_status
    edit_manager = MagicMock()

    # Configurar el comportamiento esperado del mock para que el método falle
    edit_manager.get_edit_session_status.return_value = (
        "Los últimos cambios no se han aplicado"
    )

    # Llamar al método get_edit_session_status con un identificador de encuesta
    result = edit_manager.get_edit_session_status("encuesta_id")

    # Verificar que el método devolvió el resultado esperado
    assert result == "Los últimos cambios no se han aplicado"
    # Verificar que se llamó al método get_edit_session_status con el argumento esperado
    edit_manager.get_edit_session_status.assert_called_once_with("encuesta_id")
