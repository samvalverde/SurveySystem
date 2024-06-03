from kafka import KafkaProducer, KafkaConsumer
import json

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def send_message(topic, message):
    producer.send(topic, message)
    producer.flush()


def consume_messages():
    consumer = KafkaConsumer(
        "survey-edits",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="survey-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    )

    for message in consumer:
        handle_message(message.value)


def handle_message(message):
    # Lógica para manejar los mensajes consumidos
    print(f"Message consumed: {message}")
    survey_id = message["survey_id"]
    changes = message["changes"]
    # Actualizar la encuesta con los cambios recibidos
    update_survey(survey_id, changes)
