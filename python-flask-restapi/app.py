import json
import os

from app_service import AppService
from db import Database
from flask import Flask, request

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


db = Database(
    database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
)

app = Flask(__name__)
appService = AppService(db)


@app.route("/")
def home():
    return "Conectado a la base de datos de tareas."


@app.route("/api/tasks")
def tasks():
    return appService.get_tasks()


@app.route("/api/tasks/<int:id>")
def tasks_by_id(id):
    return appService.get_tasks_by_ID(str(id))


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
