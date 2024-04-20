import json
import os
import redis
from app_service import AppService
from db import Database
from dbMongo import MongoDatabase  # Importa la clase MongoDatabase
from flask import Flask, request
from pymongo import MongoClient

from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
    verify_jwt_in_request,
)


# Configuración de la base de datos PostgreSQL
DB_HOST = os.getenv("DB_HOST_POSTGRES")  # Corrección aquí
DB_PORT = os.getenv("DB_PORT_POSTGRES")
DB_NAME = os.getenv("DB_NAME_POSTGRES")
DB_USER = os.getenv("DB_USER_POSTGRES")
DB_PASSWORD = os.getenv("DB_PASSWORD_POSTGRES")

# Inicializar la conexión a la base de datos PostgreSQL
db = Database(
    database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
)

# Configuración de la base de datos MongoDB
MONGO_HOST = os.getenv("DB_HOST_MONGO")
MONGO_PORT = os.getenv("DB_PORT_MONGO")
MONGO_USER = os.getenv("DB_USER_MONGO")
MONGO_PASSWORD = os.getenv("DB_PASSWORD_MONGO")

# Inicializar la conexión a la base de datos MongoDB
client = MongoClient(
    f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
)
mongo_db = MongoDatabase(client)

# Configuración de la base de datos Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")

# Inicializar la conexión a la base de datos Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Inicializar la instancia de AppService con ambas conexiones de base de datos
appService = AppService(db, mongo_db, redis_client)


# ------------------------------------------------------------------- Inicializar la aplicación Flask -------------------------------------------------------------------
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "1234"  # Cambia esto por tu clave secreta
jwt = JWTManager(app)

# ------------------------------------------------------------- Autenticación y Autorización -------------------------------------------------------------


# Ruta para autenticación y generación de tokens
@app.route("/auth/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Verificar si el usuario y la contraseña existen en la base de datos
    cursor = db.conn.cursor()
    cursor.execute(
        f"SELECT * FROM Usuario WHERE Username = '{username}' AND Password = '{password}';"
    )
    user_data = cursor.fetchone()
    cursor.close()

    if user_data is None:
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Crear el token de acceso para el usuario autenticado
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@app.route("/auth/register", methods=["POST"])
def create_user():
    request_data = request.get_json()
    user = request_data
    return appService.create_user(user)


def check_role(required_role):
    try:
        # Verificar que el token JWT esté presente en la solicitud
        verify_jwt_in_request()

        # Obtener la identidad del usuario desde el token JWT
        current_user = get_jwt_identity()

        # Consultar la base de datos para obtener el rol del usuario
        cursor = db.conn.cursor()
        cursor.execute(
            f"SELECT IdTipoRole FROM Usuario WHERE Username = '{current_user}';"
        )
        user_role_id = cursor.fetchone()
        cursor.close()

        if user_role_id is None:
            return False

        # Verificar si el usuario tiene el rol requerido
        return user_role_id[0] == required_role

    except Exception as e:
        # Manejar cualquier error que pueda ocurrir durante la verificación
        print(f"Error durante la verificación de roles: {str(e)}")
        return False


# --------------------------------------------------------------------------   USUARIOS   --------------------------------------------------------------------------
@app.route("/users")
@jwt_required()
def users():
    if not check_role(1):
        return (
            jsonify({"error": "Usuario no autorizado para realizar esta acción"}),
            403,
        )
    return appService.get_users()


@app.route("/users/<int:id>")
def user_by_id(id):
    return appService.get_User_by_ID(str(id))


@app.route("/users/<int:id>", methods=["PUT"])
@jwt_required()
def update_user(id):
    verify_jwt_in_request()
    # Obtener el ID del usuario actual desde el token JWT
    current_user_id = get_jwt_identity()

    # Verificar si el usuario tiene permiso para realizar la actualización
    if not check_role(1) and current_user_id != id:
        return jsonify({"error": "Usuario no autorizado para editar este perfil"}), 403

    # Si pasó la verificación, proceder con la actualización del usuario
    request_data = request.get_json()
    return appService.update_user(request_data, str(id))


@app.route("/users/<int:id>", methods=["DELETE"])
@jwt_required()  # Requiere autenticación JWT
def delete_user(id):
    if not check_role(1):
        return (
            jsonify({"error": "Usuario no autorizado para realizar esta acción"}),
            403,
        )
    return appService.delete_user(str(id))


# --------------------------------------------------------------------------   ENCUESTAS    --------------------------------------------------------------------------
@app.route("/surveys")
def encuestas():
    return appService.get_encuestas()  # solo las que tengan publicadas


@app.route("/surveys/<int:id>")
def encuesta_by_id(id):

    result = appService.get_encuesta_by_ID(str(id))
    if result:
        return result
    else:
        return jsonify({"error": "No existe una encuesta con este ID"}), 500


@app.route("/surveys", methods=["POST"])
@jwt_required()  # Requiere autenticación JWT
def create_encuesta():
    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para crear encuestas"}),
            403,
        )  # si no es admin ni creador no puede crear encuestas

    request_data = request.get_json()
    encuesta = request_data

    # Llama al método del servicio para crear la encuesta
    result = appService.create_encuesta(encuesta)

    # Verifica si la creación de la encuesta fue exitosa
    if result:
        return jsonify({"message": "Encuesta creada correctamente"}), 201
    else:
        return jsonify({"error": "Error al crear la encuesta"}), 500


@app.route("/surveys/<int:id>", methods=["PUT"])
@jwt_required()  # Requiere autenticación JWT
def update_encuesta(id):

    if check_role(3):
        return jsonify({"error": "Usuario no autorizado para crear encuestas"}), 403

    request_data = request.get_json()
    result = appService.update_encuesta(request_data, str(id))
    # Verifica si la creación de la encuesta fue exitosa
    if result:
        return jsonify({"message": "Encuesta modificada correctamente"}), 201
    else:
        return jsonify({"error": "Error al modificar la encuesta"}), 500


@app.route("/surveys/<int:id>", methods=["DELETE"])
@jwt_required()  # Requiere autenticación JWT
def delete_encuesta(id):
    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para crear encuestas"}),
            403,
        )  # si no es admin ni creador no puede borrar encuestas
    return appService.delete_encuesta(str(id))


@app.route("/surveys/<int:id>/publish", methods=["POST"])
@jwt_required()  # Requiere autenticación JWT
def publish_survey(id):
    # Verificar si el usuario tiene permiso para publicar la encuesta
    current_user = get_jwt_identity()
    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para publicar esta encuesta"}),
            403,
        )
    # Llama al método del servicio para publicar la encuesta
    result = appService.publish_survey(str(id))

    if result:
        return jsonify({"message": "Encuesta publicada correctamente"}), 200
    else:
        return jsonify({"error": "Error al publicar la encuesta"}), 500


# --------------------------------------------------------------- PREGUNTAS DE ENCUESTAS ---------------------------------------------------------------


@app.route("/surveys/<int:id>/questions", methods=["POST"])
@jwt_required()  # Requiere autenticación JWT
def add_question(id):
    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para crear encuestas"}),
            403,
        )  # si no es admin ni creador no puede
    request_data = request.get_json()
    # Llama al método del servicio para agregar la pregunta a la encuesta
    result = appService.add_question(str(id), request_data)

    if result:
        return jsonify({"message": "Pregunta agregada correctamente"}), 201
    else:
        return jsonify({"error": "Error al agregar la pregunta"}), 500


@app.route("/surveys/<int:id>/questions", methods=["GET"])
def get_questions(id):
    # Llama al método del servicio para obtener todas las preguntas de la encuesta
    questions = appService.get_questions(str(id))
    return jsonify(questions)


@app.route("/surveys/<int:id>/questions/<questionId>", methods=["PUT"])
@jwt_required()  # Requiere autenticación JWT
def update_question(id, questionId):
    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para crear encuestas"}),
            403,
        )  # si no es admin ni creador no puede
    request_data = request.get_json()
    # Llama al método del servicio para actualizar la pregunta de la encuesta
    result = appService.update_question(str(id), int(questionId), request_data)

    if result:
        return jsonify({"message": "Pregunta actualizada correctamente"}), 200
    else:
        return jsonify({"error": "Error al actualizar la pregunta"}), 500


@app.route("/surveys/<int:id>/questions/<questionId>", methods=["DELETE"])
@jwt_required()  # Requiere autenticación JWT
def delete_question(id, questionId):
    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para crear encuestas"}),
            403,
        )  # si no es admin ni creador no
    # Llama al método del servicio para eliminar la pregunta de la encuesta
    result = appService.delete_question(str(id), int(questionId))

    if result:
        return jsonify({"message": "Pregunta eliminada correctamente"}), 200
    else:
        return jsonify({"error": "Error al eliminar la pregunta"}), 500


# ------------------------------------------------------------- RESPUESTAS -------------------------------------------------------------


@app.route("/surveys/<string:id>/responses", methods=["POST"])
def submit_response(id):
    try:
        respuesta = request.get_json()
        encuesta_id = str(id)
        usuario_id = respuesta["usuario_id"]
        response_data = respuesta["respuestas"]

        if not encuesta_id or not usuario_id or not response_data:
            return jsonify({"error": "Datos incompletos"}), 400

        result = appService.submit_response(encuesta_id, usuario_id, response_data)

        if result:
            return jsonify({"message": "Respuesta enviada correctamente"}), 201
        else:
            return jsonify({"error": "Error al enviar la respuesta"}), 500

    except Exception as e:
        print(f"Error en la solicitud POST /surveys/{id}/responses: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


@app.route("/surveys/<string:id>/responses", methods=["GET"])
@jwt_required()  # Requiere autenticación JWT
def get_responses(id):

    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para crear encuestas"}),
            403,
        )  # si no es admin ni creador no puede

    try:
        encuesta_id = str(id)

        if not encuesta_id:
            return jsonify({"error": "ID de encuesta faltante"}), 400

        responses = appService.get_responses(encuesta_id)

        if responses is not None:
            return jsonify(responses), 200
        else:
            return jsonify({"error": "Error al obtener las respuestas"}), 500

    except Exception as e:
        print(f"Error en la solicitud GET /surveys/{id}/responses: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


# ------------------------------------------------------------- ENCUESTADOS -------------------------------------------------------------
@app.route("/respondents", methods=["POST"])
def create_respondent():
    request_data = request.get_json()
    respondent = request_data
    return appService.create_respondent(respondent)


@app.route("/respondents")
def respondents():
    if not check_role(1):
        return (
            jsonify({"error": "Usuario no autorizado para realizar esta acción"}),
            403,
        )
    return appService.get_respondents()


@app.route("/respondents/<int:id>")
def respondent_by_id(id):
    return appService.get_respondent_by_ID(str(id))


@app.route("/respondents/<int:id>", methods=["PUT"])
def update_respondent(id):
    verify_jwt_in_request()
    # Obtener el ID del usuario actual desde el token JWT
    current_respondent_id = get_jwt_identity()

    # Verificar si el usuario tiene permiso para realizar la actualización
    if not check_role(1) and current_respondent_id != id:
        return jsonify({"error": "Usuario no autorizado para editar este perfil"}), 403

    # Si pasó la verificación, proceder con la actualización del usuario
    request_data = request.get_json()
    return appService.update_respondent(request_data, str(id))


@app.route("/respondents/<int:id>", methods=["DELETE"])
def delete_respondent(id):
    return appService.delete_respondent(str(id))


# ------------------------------------------------------------- ANÁLISIS DE ENCUESTAS -------------------------------------------------------------
@app.route("/surveys/<string:id>/analysis", methods=["GET"])
@jwt_required()  # Requiere autenticación JWT
def generate_analysis(id):

    if check_role(3):
        return (
            jsonify({"error": "Usuario no autorizado para crear encuestas"}),
            403,
        )  # si no es admin ni creador no puede crear encuestas

    try:
        encuesta_id = str(id)

        if not encuesta_id:
            return jsonify({"error": "ID de encuesta faltante"}), 400

        success, analysis = appService.generate_analysis(encuesta_id)

        if success:
            return jsonify({"analysis": analysis}), 200
        else:
            return jsonify({"error": "Error al generar el análisis"}), 400

    except Exception as e:
        print(f"Error en la solicitud GET /surveys/{id}/analysis: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
