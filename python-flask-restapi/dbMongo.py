from pymongo import MongoClient
from bson import ObjectId
import json


class MongoDatabase:
    def __init__(self, mongoClient: MongoClient):
        self.client = mongoClient
        self.database = self.client["EncuestasDB"]
        self.collection = self.database["encuestas"]

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

    def _convert_object_ids(self, data): ###
        # Convertir ObjectId a una representación serializable si es necesario
        if "_id" in data:
            data["_id"] = str(data["_id"])

    def insert_pregunta(self, pregunta_data): ###
        # Convertir ObjectId a una representación serializable si es necesario
        self._convert_object_ids(pregunta_data)
        self.collection.insert_one(pregunta_data)

    def get_preguntas_by_encuesta_id(self, encuesta_id):
        preguntas = list(self.collection.find({"encuesta_id": encuesta_id}))
        # Convertir ObjectId a una representación serializable si es necesario
        for pregunta in preguntas:
            self._convert_object_ids(pregunta)
        return preguntas

    def get_pregunta_by_id(self, encuesta_id, pregunta_id):
        pregunta = self.collection.find_one({"encuesta_id": encuesta_id, "pregunta_id": pregunta_id})
        # Convertir ObjectId a una representación serializable si es necesario
        self._convert_object_ids(pregunta)
        return pregunta

    def update_pregunta(self, pregunta_id, updated_pregunta_json): ###
        # Convierte el JSON a un diccionario
        updated_pregunta = json.loads(updated_pregunta_json)
        # Verifica que updated_pregunta sea un diccionario
        if isinstance(updated_pregunta, dict):
            # Elimina el pregunta_id del diccionario
            if "pregunta_id" in updated_pregunta:
                del updated_pregunta["pregunta_id"]
            # Realiza la actualización utilizando el modificador $set
            self.collection.update_one(
                {"pregunta_id": pregunta_id}, {"$set": updated_pregunta}
            )
            return updated_pregunta
        else:
            return "Error: El JSON proporcionado no es válido"
    
    def delete_pregunta(self, encuesta_id, pregunta_id):
        result = self.collection.delete_one({"encuesta_id": encuesta_id, "pregunta_id": pregunta_id})
        return result.deleted_count
