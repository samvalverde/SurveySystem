from pymongo import MongoClient

class SurveyService:
    def __init__(self, mongo_uri):
        self.client = MongoClient(mongo_uri)
        self.db = self.client['EncuestasDB']
        self.surveys_collection = self.db['encuestas']

    def get_survey_by_id(self, survey_id):
        return self.surveys_collection.find_one({'id_encuesta': survey_id})