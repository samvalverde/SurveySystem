import redis
import json
from db import Database
from dbMongo import MongoDatabase  # Importa la clase MongoDatabase
from dbMongo import MongoDatabase
from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic

import os
import time


class AppService:
    def __init__(
        self,
        database: Database,
        mongo_database: MongoDatabase,
        redis_client: redis.StrictRedis,
    ):
        self.database = database
        self.mongo_database = mongo_database
        self.redis_client = redis_client
        kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

        self.producer = self.initialize_kafka_producer(kafka_bootstrap_servers)
        self.consumer = self.initialize_kafka_consumer(kafka_bootstrap_servers)
        self.last_changes = "last_changes"
        self.kafka_admin_client = KafkaAdminClient(
            bootstrap_servers=kafka_bootstrap_servers
        )

    def initialize_kafka_producer(self, kafka_bootstrap_servers):
        while True:
            try:
                producer = KafkaProducer(
                    bootstrap_servers=kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
                return producer
            except Exception as e:
                print(f"KafkaProducer connection failed: {e}, retrying in 5 seconds...")
                time.sleep(5)

    def initialize_kafka_consumer(self, kafka_bootstrap_servers):
        while True:
            try:
                consumer = KafkaConsumer(
                    "topic_encuesta_edicion",
                    bootstrap_servers=kafka_bootstrap_servers,
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    group_id="my-group",
                    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                )
                return consumer
            except Exception as e:
                print(f"KafkaConsumer connection failed: {e}, retrying in 5 seconds...")
                time.sleep(5)

    def send_changes_to_kafka(self, changes):
        self.producer.send("topic_encuesta_edicion", value=changes)
        self.last_changes = changes
        self.producer.flush()

    def get_kafka_changes(self, encuesta_id):
        for message in self.consumer:
            if message.value.get("id_encuesta") == str(encuesta_id):
                return message.value
        return None

    def submit_changes(self, encuesta_id):
        changes = self.get_kafka_changes(encuesta_id)
        self.mongo_database.update_encuesta(str(encuesta_id), changes)

    def start_edit_session(self, encuesta_id):
        try:
            topic_name = str(encuesta_id)
            topic_list = self.kafka_admin_client.list_topics()

            if topic_name in topic_list:
                return False, "La sesión ya existe"

            new_topic = NewTopic(
                name=topic_name, num_partitions=1, replication_factor=1
            )
            self.kafka_admin_client.create_topics([new_topic])
            return True, "Sesión de edición iniciada"
        except Exception as e:
            print(f"Error al iniciar la sesión de edición: {str(e)}")
            return False, f"Error al iniciar la sesión de edición: {str(e)}"

    def get_edit_session_status(self, encuesta_id):
        # Obtiene la encuesta guardada en MongoDB
        encuesta_db = self.mongo_database.get_encuesta_by_id(encuesta_id)
        if encuesta_db:
            # Obtiene los cambios guardados temporalmente
            changes = self.last_changes
            if not changes:
                return "Primero debe crearse una sesión"
            changes["_id"] = "a"
            encuesta_db["_id"] = "a"
            # Convierte los objetos JSON a cadenas de texto
            changes_str = json.dumps(changes, sort_keys=True)
            encuesta_db_str = json.dumps(encuesta_db, sort_keys=True)

            # Compara las cadenas de texto
            if changes_str == encuesta_db_str:
                return "Últimos cambios aplicados"
            else:
                return "Los últimos cambios no se han aplicado"
        else:
            return "Encuesta no encontrada en la base de datos"

    # ------------------------------------------------------------- REDIS -------------------------------------------------------------
    # funcion para limpiar caché
    def clear_cache(self, cache_key):
        try:
            self.redis_client.delete(cache_key)
            print(f"Caché para la clave '{cache_key}' limpiada correctamente.")
        except Exception as e:
            print(f"Error al limpiar la caché para la clave '{cache_key}': {str(e)}")

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
        self.clear_cache("users")
        return data

    def create_user(self, task):
        self.database.create_user(task)
        self.clear_cache("users")
        return task

    def update_user(self, request_user, request_user_id):
        self.database.update_user(request_user, request_user_id)
        self.clear_cache("users")
        return request_user

    def delete_user(self, request_user_id):
        self.database.delete_user(request_user_id)
        self.clear_cache("users")
        return request_user_id

    def login_user(self, username, password):
        data = self.database.login_user(username, password)
        return data

    # seccion de encuestas
    def get_encuestas(self):
        cache_key = "encuestas"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        data = self.mongo_database.get_encuestas()
        # Convertir los datos a un formato adecuado para caché
        cached_data = json.dumps(data)
        # Almacenar en caché los datos con una expiración de 1 hora (3600 segundos)
        self.redis_client.setex(cache_key, 3600, cached_data)
        return data

    def get_encuesta_by_ID(self, encuesta_id):
        data = self.mongo_database.get_encuesta_by_id(encuesta_id)
        return data

    def create_encuesta(self, encuesta):
        self.mongo_database.insert_encuesta(encuesta)
        self.database.insert_encuesta(encuesta)
        self.clear_cache("encuestas")
        return encuesta

    def update_encuesta(self, updated_encuesta, encuesta_id):
        self.mongo_database.update_encuesta(encuesta_id, updated_encuesta)
        self.database.update_encuesta(encuesta_id, updated_encuesta)
        self.clear_cache("encuestas")
        return updated_encuesta

    def delete_encuesta(self, encuesta_id):
        self.clear_cache("encuestas")
        self.mongo_database.delete_encuesta(encuesta_id)
        self.database.delete_encuesta(encuesta_id)
        return encuesta_id

    def publish_survey(self, id):
        self.clear_cache("encuestas")
        self.mongo_database.publish_encuesta(id)
        return id

    # seccion de preguntas
    def add_question(self, survey_id, question_data):
        self.clear_cache(f"questions:{survey_id}")
        return self.mongo_database.add_question(survey_id, question_data)

    def get_questions(self, survey_id):
        cache_key = f"questions:{survey_id}"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            # Si hay datos en caché, se devuelven después de cargarlos y convertirlos de JSON a Python dict
            return json.loads(cached_data)
        else:
            # Si no hay datos en caché, se obtienen de la base de datos MongoDB
            data = self.mongo_database.get_questions(survey_id)
            # Convertir los datos a formato JSON antes de almacenarlos en caché
            json_data = json.dumps(data)
            self.redis_client.set(cache_key, json_data)
            return data

    def update_question(self, survey_id, question_id, updated_question_data):
        self.clear_cache(f"questions:{survey_id}")
        return self.mongo_database.update_question(
            survey_id, question_id, updated_question_data
        )

    def delete_question(self, survey_id, question_id):
        self.clear_cache(f"questions:{survey_id}")
        return self.mongo_database.delete_question(survey_id, question_id)

    # Seccion de encuestados

    def get_respondents(self):
        cache_key = "respondents"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            # Si hay datos en caché, se devuelven después de cargarlos y convertirlos de JSON a Python dict
            return json.loads(cached_data)
        else:
            # Si no hay datos en caché, se obtienen de la base de datos
            data = self.database.get_respondents()
            # Convertir los datos a formato JSON antes de almacenarlos en caché
            json_data = json.dumps(data)
            self.redis_client.set(cache_key, json_data)
            return data

    def get_respondent_by_ID(self, request_respondent_id):
        data = self.database.get_respondent_by_ID(request_respondent_id)
        return data

    def create_respondent(self, respondent):
        self.clear_cache("respondents")
        self.database.create_respondent(respondent)
        return respondent

    def update_respondent(self, request_respondent, request_respondent_id):
        self.clear_cache("respondents")
        self.database.update_respondent(request_respondent, request_respondent_id)
        return request_respondent

    def delete_respondent(self, request_respondent_id):
        self.clear_cache("respondents")
        self.database.delete_respondent(request_respondent_id)
        return request_respondent_id

    # Seccion de respuestas
    def submit_response(self, encuesta_id, usuario_id, response_data):
        self.clear_cache(f"responses:{encuesta_id}")
        return self.mongo_database.submit_response(
            encuesta_id, usuario_id, response_data
        )

    def get_responses(self, encuesta_id):
        cache_key = f"responses:{encuesta_id}"
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            # Si hay datos en caché, se devuelven después de cargarlos y convertirlos de JSON a Python dict
            return json.loads(cached_data)
        else:
            # Si no hay datos en caché, se obtienen de la base de datos
            data = self.mongo_database.get_responses(encuesta_id)
            # Convertir los datos a formato JSON antes de almacenarlos en caché
            json_data = json.dumps(data)
            self.redis_client.set(cache_key, json_data)
            return data

    # Seccion de reportes y analisis
    def generate_analysis(self, encuesta_id):
        return self.mongo_database.generate_analysis(encuesta_id)
