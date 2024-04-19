import json
import os

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
    get_jwt,
)


# Configuración de la base de datos PostgreSQL
DB_HOST = os.getenv("DB_HOST_POSTGRES")  # Corrección aquí
DB_PORT = os.getenv("DB_PORT_POSTGRES")
DB_NAME = os.getenv("DB_NAME_POSTGRES")
DB_USER = os.getenv("DB_USER_POSTGRES")
DB_PASSWORD = os.getenv("DB_PASSWORD_POSTGRES")

# Configuración de la base de datos MongoDB
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")

# Inicializar la conexión a la base de datos PostgreSQL
db = Database(
    database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
)

# Inicializar la conexión a la base de datos MongoDB
client = MongoClient("mongo", 27017, username="root", password="password")
mongo_db = MongoDatabase(client)

# Inicializar la instancia de AppService con ambas conexiones de base de datos
appService = AppService(db, mongo_db)

# Inicializar la aplicación Flask
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


# --------------------------------------------------------------------------   Usuarios   --------------------------------------------------------------------------
@app.route("/users")
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
def delete_user(id):
    return appService.delete_user(str(id))


# --------------------------------------------------------------------------   Encuestas    --------------------------------------------------------------------------
@app.route("/surveys")
def encuestas():
    return appService.get_encuestas()


@app.route("/surveys/<int:id>")
def encuesta_by_id(id):
    return appService.get_encuesta_by_ID(str(id))


@app.route("/surveys", methods=["POST"])
@jwt_required()  # Requiere autenticación JWT
def create_encuesta():
    if check_role(3):
        return jsonify({"error": "Usuario no autorizado para crear encuestas"}), 403

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
def update_encuesta(id):
    request_data = request.get_json()
    result = appService.update_encuesta(request_data, str(id))
    # Verifica si la creación de la encuesta fue exitosa
    if result:
        return jsonify({"message": "Encuesta modificada correctamente"}), 201
    else:
        return jsonify({"error": "Error al modificar la encuesta"}), 500


@app.route("/surveys/<int:id>", methods=["DELETE"])
def delete_encuesta(id):
    return appService.delete_encuesta(str(id))


@app.route("/encuestassql")
def encuestassql():
    return appService.get_encuestassql()


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
    result = appService.publish_survey(id)

    if result:
        return jsonify({"message": "Encuesta publicada correctamente"}), 200
    else:
        return jsonify({"error": "Error al publicar la encuesta"}), 500


# --------------------------------------------------------------- Preguntas de Encuestas ---------------------------------------------------------------


@app.route("/surveys/<int:id>/questions", methods=["POST"])
@jwt_required()  # Requiere autenticación JWT
def add_question(id):

    request_data = request.get_json()
    # Llama al método del servicio para agregar la pregunta a la encuesta
    result = appService.add_question(id, request_data)

    if result:
        return jsonify({"message": "Pregunta agregada correctamente"}), 201
    else:
        return jsonify({"error": "Error al agregar la pregunta"}), 500


@app.route("/surveys/<int:id>/questions", methods=["GET"])
def get_questions(id):
    # Llama al método del servicio para obtener todas las preguntas de la encuesta
    questions = appService.get_questions(id)
    return jsonify(questions)


@app.route("/surveys/<int:id>/questions/<questionId>", methods=["PUT"])
@jwt_required()  # Requiere autenticación JWT
def update_question(id, questionId):

    request_data = request.get_json()
    # Llama al método del servicio para actualizar la pregunta de la encuesta
    result = appService.update_question(id, questionId, request_data)

    if result:
        return jsonify({"message": "Pregunta actualizada correctamente"}), 200
    else:
        return jsonify({"error": "Error al actualizar la pregunta"}), 500


@app.route("/surveys/<int:id>/questions/<questionId>", methods=["DELETE"])
@jwt_required()  # Requiere autenticación JWT
def delete_question(id, questionId):

    # Llama al método del servicio para eliminar la pregunta de la encuesta
    result = appService.delete_question(id, questionId)

    if result:
        return jsonify({"message": "Pregunta eliminada correctamente"}), 200
    else:
        return jsonify({"error": "Error al eliminar la pregunta"}), 500
