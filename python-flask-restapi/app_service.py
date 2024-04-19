import redis
import json
from db import Database
from dbMongo import MongoDatabase  # Importa la clase MongoDatabase


class AppService:
    def __init__(
        self,
        database: Database,
        mongo_database: MongoDatabase,
        redis_client: redis.StrictRedis,
    ):
        self.database = database
        self.mongo_database = mongo_database
        self.redis_client = redis.StrictRedis(host="redis", port=6379, db=0)

    # seccion de usuarios
    def get_users(self):
        cache_key = "users"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        else:
            data = self.database.get_users()
            self.redis_client.set(cache_key, json.dumps(data))
            return data

    def get_User_by_ID(self, request_user_id):
        data = self.database.get_User_by_ID(request_user_id)
        return data

    def create_user(self, task):
        self.database.create_user(task)
        return task

    def update_user(self, request_user, request_user_id):
        self.database.update_user(request_user, request_user_id)
        return request_user

    def delete_user(self, request_user_id):
        self.database.delete_user(request_user_id)
        return request_user_id

    # seccion de encuestas
    def get_encuestas(self):
        # Clave para almacenar en caché los datos de las encuestas
        cache_key = "encuestas"

        # Intentar recuperar los datos de la caché
        cached_data = self.redis_client.get(cache_key)

        if cached_data:
            # Si los datos están en caché, devolverlos directamente
            return cached_data.decode("utf-8")

        # Si los datos no están en caché, obtenerlos de la base de datos
        data = self.mongo_database.get_encuestas()

        # Almacenar los datos en caché para futuras solicitudes
        self.redis_client.set(cache_key, data)

        return data

    def get_encuesta_by_ID(self, encuesta_id):
        data = self.mongo_database.get_encuesta_by_id(encuesta_id)
        return data

    def create_encuesta(self, encuesta):
        self.mongo_database.insert_encuesta(encuesta)
        self.database.insert_encuesta(encuesta)
        return encuesta

    def update_encuesta(self, updated_encuesta, encuesta_id):
        self.mongo_database.update_encuesta(encuesta_id, updated_encuesta)
        self.database.update_encuesta(encuesta_id, updated_encuesta)
        return updated_encuesta

    def delete_encuesta(self, encuesta_id):
        self.mongo_database.delete_encuesta(encuesta_id)
        self.database.delete_encuesta(encuesta_id)
        return encuesta_id

    def publish_survey(self, id):
        self.mongo_database.publish_encuesta(id)
        return id

    # seccion de preguntas
    def add_question(self, survey_id, question_data):
        return self.mongo_database.add_question(survey_id, question_data)

    def get_questions(self, survey_id):
        cache_key = f"questions:{survey_id}"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        else:
            data = self.mongo_database.get_questions(survey_id)
            self.redis_client.set(cache_key, json.dumps(data))
            return data

    def update_question(self, survey_id, question_id, updated_question_data):
        return self.mongo_database.update_question(
            survey_id, question_id, updated_question_data
        )

    def delete_question(self, survey_id, question_id):
        return self.mongo_database.delete_question(survey_id, question_id)

    # Seccion de encuestados

    def get_respondents(self):
        cache_key = "respondents"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        else:
            data = self.database.get_respondents()
            self.redis_client.set(cache_key, json.dumps(data))
            return data

    def get_respondent_by_ID(self, request_respondent_id):
        cache_key = f"respondent:{request_respondent_id}"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        else:
            data = self.database.get_respondent_by_ID(request_respondent_id)
            self.redis_client.set(cache_key, json.dumps(data))
            return data

    def create_respondent(self, respondent):
        self.database.create_respondent(respondent)
        return respondent

    def update_respondent(self, request_respondent, request_respondent_id):
        self.database.update_respondent(request_respondent, request_respondent_id)
        return request_respondent

    def delete_respondent(self, request_respondent_id):
        self.database.delete_respondent(request_respondent_id)
        return request_respondent_id

    # Seccion de respuestas
    def submit_response(self, encuesta_id, usuario_id, response_data):
        return self.mongo_database.submit_response(
            encuesta_id, usuario_id, response_data
        )

    def get_responses(self, encuesta_id):
        cache_key = f"responses:{encuesta_id}"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        else:
            data = self.mongo_database.get_responses(encuesta_id)
            self.redis_client.set(cache_key, json.dumps(data))
            return data

    # Seccion de reportes y analisis
    def generate_analysis(self, encuesta_id):
        return self.mongo_database.generate_analysis(encuesta_id)
