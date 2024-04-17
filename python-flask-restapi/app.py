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


# Ruta protegida que requiere autenticación
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/auth/register", methods=["POST"])
def create_user():
    request_data = request.get_json()
    user = request_data
    return appService.create_user(user)


@app.route("/users")
def users():
    return appService.get_users()


@app.route("/users/<int:id>")
def user_by_id(id):
    return appService.get_User_by_ID(str(id))


@app.route("/users/<int:id>", methods=["PUT"])
def update_user(id):
    request_data = request.get_json()
    return appService.update_user(request_data, str(id))


@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    return appService.delete_user(str(id))


# Rutas para la base de datos MongoDB
@app.route("/api/surveys")
def encuestas():
    return appService.get_encuestas()


@app.route("/api/surveys/<int:id>")
def encuesta_by_id(id):
    return appService.get_encuesta_by_ID(str(id))


@app.route("/api/surveys", methods=["POST"])
@jwt_required()  # Requiere autenticación JWT
def create_encuesta():
    current_user = (
        get_jwt_identity()
    )  # Obtiene la identidad del usuario desde el token JWT
    if not current_user:
        return (
            jsonify({"error": "Usuario no autenticado"}),
            401,
        )  # Devuelve un error si el usuario no está autenticado

    request_data = request.get_json()
    encuesta = request_data

    # Llama al método del servicio para crear la encuesta
    result = appService.create_encuesta(encuesta)

    # Verifica si la creación de la encuesta fue exitosa
    if result:
        return jsonify({"message": "Encuesta creada correctamente"}), 201
    else:
        return jsonify({"error": "Error al crear la encuesta"}), 500


@app.route("/api/surveys/<int:id>", methods=["PUT"])
def update_encuesta(id):
    request_data = request.get_json()
    return appService.update_encuesta(request_data, str(id))


@app.route("/api/surveys/<int:id>", methods=["DELETE"])
def delete_encuesta(id):
    return appService.delete_encuesta(str(id))


@app.route("/api/surveys/<int:id>/questions", methods=["POST"])
@jwt_required()  
def create_pregunta(id):
    request_data = request.get_json()
    pregunta = request_data
    result = appService.create_pregunta(pregunta)
    if result:
        return jsonify({"message": "Pregunta creada correctamente"}), 201
    else:
        return jsonify({"error": "Error al crear la pregunta"}), 500


@app.route("/api/surveys/<int:id>/questions", methods=["GET"])
@jwt_required()
def get_preguntas(id):
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@app.route("/api/surveys/<int:id>/questions/<int:questionId>", methods=["PUT"])
def update_pregunta(id, questionId):
    request_data = request.get_json()
    return appService.update_pregunta(request_data, str(id), str(questionId))


@app.route("/api/surveys/<int:id>/questions/<int:questionId>", methods=["DELETE"])
def delete_pregunta(id, questionId):
    return appService.delete_pregunta(str(id), str(questionId))
