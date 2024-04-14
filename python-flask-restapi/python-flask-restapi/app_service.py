import json
from db import Database
from dbMongo import MongoDatabase  # Importa la clase MongoDatabase


class AppService:
    def __init__(self, database: Database, mongo_database: MongoDatabase):
        self.database = database
        self.mongo_database = mongo_database

    # Métodos para la base de datos PostgreSQL
    def get_tasks(self):
        data = self.database.get_tasks()
        return data

    def get_task_by_ID(self, request_task_id):
        data = self.database.get_tasks_by_ID(request_task_id)
        return data

    def create_task(self, task):
        self.database.create_task(task)
        return task

    def update_task(self, request_task, request_task_id):
        self.database.update_task(request_task, request_task_id)
        return request_task

    def delete_task(self, request_task_id):
        self.database.delete_task(request_task_id)
        return request_task_id

    # Métodos para la base de datos MongoDB
    def get_encuestas(self):
        data = self.mongo_database.get_encuestas()
        return data

    def get_encuesta_by_ID(self, encuesta_id):
        data = self.mongo_database.get_encuesta_by_id(encuesta_id)
        return data

    def create_encuesta(self, encuesta):
        self.mongo_database.insert_encuesta(encuesta)
        return encuesta

    def update_encuesta(self, encuesta_id, updated_encuesta):
        self.mongo_database.update_encuesta(encuesta_id, updated_encuesta)
        return updated_encuesta

    def delete_encuesta(self, encuesta_id):
        self.mongo_database.delete_encuesta(encuesta_id)
        return encuesta_id
