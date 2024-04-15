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
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "user" or password != "password":
        return jsonify({"error": "Credenciales inválidas"}), 401
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


# Ruta protegida que requiere autenticación
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


# Rutas para la base de datos PostgreSQL
@app.route("/")
def home():
    return "Conectado a la base de datos de tareas."


@app.route("/api/tasks")
def tasks():
    return appService.get_tasks()


@app.route("/api/tasks/<int:id>")
def tasks_by_id(id):
    return appService.get_task_by_ID(str(id))


@app.route("/api/tasks", methods=["POST"])
def create_task():
    request_data = request.get_json()
    task = request_data
    return appService.create_task(task)


@app.route("/api/tasks/<int:id>", methods=["PUT"])
def update_task(id):
    request_data = request.get_json()
    return appService.update_task(request_data, str(id))


@app.route("/api/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):
    return appService.delete_task(str(id))

##############################################################################################
##############################################################################################
##############################################################################################
# Rutas para la base de datos MongoDB
@app.route("/api/encuestas")  #SIRVE
def encuestas():
    return appService.get_encuestas()


@app.route("/api/encuestas/<int:id>")   #SIRVE
def encuesta_by_id(id):
    return appService.get_encuesta_by_ID(str(id))


@app.route("/api/encuestas", methods=["POST"])
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


@app.route("/api/encuestas/<int:id>", methods=["PUT"])    #SIRVE PERO NO
def update_encuesta(id):
    request_data = request.get_json()
    return appService.update_encuesta(request_data, str(id))


@app.route("/api/encuestas/<int:id>", methods=["DELETE"])   #SIRVE
def delete_encuesta(id):
    return appService.delete_encuesta(str(id))
