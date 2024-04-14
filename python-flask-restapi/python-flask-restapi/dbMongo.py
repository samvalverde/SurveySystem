from pymongo import MongoClient


class MongoDatabase:
    def __init__(self, mongoClient: MongoClient):
        self.client = mongoClient
        self.database = self.client["EncuestasDB"]
        self.collection = self.database["encuestas"]

    def insert_encuesta(self, encuesta_data):
        self.collection.insert_one(encuesta_data)

    def get_encuestas(self):
        return list(self.collection.find())

    def get_encuesta_by_id(self, encuesta_id):
        return self.collection.find_one({"id_encuesta": encuesta_id})

    def update_encuesta(self, encuesta_id, updated_encuesta):
        self.collection.update_one(
            {"id_encuesta": encuesta_id}, {"$set": updated_encuesta}
        )
        return updated_encuesta

    def delete_encuesta(self, encuesta_id):
        self.collection.delete_one({"id_encuesta": encuesta_id})
        return encuesta_id
