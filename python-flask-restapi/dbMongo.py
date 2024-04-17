from pymongo import MongoClient
from bson import ObjectId
import json


class MongoDatabase:
    def __init__(self, mongoClient: MongoClient):
        self.client = mongoClient
        self.database = self.client["EncuestasDB"]
        self.collection = self.database["encuestas"]

    def insert_encuesta(self, encuesta_data):
        # Convertir ObjectId a una representación serializable si es necesario
        self._convert_object_ids(encuesta_data)
        self.collection.insert_one(encuesta_data)

    def get_encuestas(self):
        encuestas = list(self.collection.find())
        # Convertir ObjectId a una representación serializable si es necesario
        for encuesta in encuestas:
            self._convert_object_ids(encuesta)
        return encuestas

    def get_encuesta_by_id(self, encuesta_id):
        encuesta = self.collection.find_one({"id_encuesta": encuesta_id})
        # Convertir ObjectId a una representación serializable si es necesario
        self._convert_object_ids(encuesta)
        return encuesta

    def update_encuesta(self, encuesta_id, updated_encuesta_json):
        self.collection.delete_one({"id_encuesta": encuesta_id})
        self._convert_object_ids(updated_encuesta_json)
        self.collection.insert_one(updated_encuesta_json)
        return updated_encuesta_json

    def delete_encuesta(self, encuesta_id):
        result = self.collection.delete_one({"id_encuesta": encuesta_id})
        return result.deleted_count

    def _convert_object_ids(self, data):
        # Convertir ObjectId a una representación serializable si es necesario
        if "_id" in data:
            data["_id"] = str(data["_id"])
