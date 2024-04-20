from pymongo import MongoClient

'''
class MongoDatabase:
    def __init__(self, mongoClient: MongoClient):
        self.client = mongoClient
        self.database = self.client["EncuestasDB"]
        self.collection = self.database["encuestas"]
'''

class SurveyService:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.database = self.client['EncuestasDB']
        self.surveys_collection = self.database['encuestas']

    def get_survey_by_id(self, survey_id):
        return self.surveys_collection.find_one({'id_encuesta': survey_id})