from pymongo import MongoClient


# Clase para interactuar con la base de datos MongoDB
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

        if encuesta:
            # Convertir ObjectId a una representación serializable si es necesario
            self._convert_object_ids(encuesta)

        return encuesta

    def update_encuesta(self, encuesta_id, updated_encuesta_data):
        # Convertir ObjectId a una representación serializable si es necesario
        self._convert_object_ids(updated_encuesta_data)

        # Actualizar el documento de la encuesta
        result = self.collection.update_one(
            {"id_encuesta": encuesta_id}, {"$set": updated_encuesta_data}
        )

        # Verificar si la actualización fue exitosa
        if result.modified_count > 0:
            return updated_encuesta_data
        else:
            return None

    def delete_encuesta(self, encuesta_id):
        result = self.collection.delete_one({"id_encuesta": encuesta_id})
        return result.deleted_count

    def _convert_object_ids(self, data):
        # Convertir ObjectId a una representación serializable si es necesario
        if "_id" in data:
            data["_id"] = str(data["_id"])

    def update_encuesta_key(self, encuesta_id, key, value):
        try:
            # Obtener la encuesta por su ID
            encuesta = self.collection.find_one({"id_encuesta": encuesta_id})

            if encuesta:
                # Actualizar la clave específica en la encuesta
                encuesta[key] = value

                # Guardar los cambios en la base de datos
                result = self.collection.update_one(
                    {"id_encuesta": encuesta_id}, {"$set": encuesta}
                )

                # Verificar si la actualización fue exitosa
                return result.modified_count > 0
            else:
                return False
        except Exception as e:
            print(f"Error al actualizar la encuesta: {str(e)}")
            return False

    def publish_encuesta(self, encuesta_id):
        try:
            # Llamar a update_encuesta_key para establecer publica en True
            return self.update_encuesta_key(encuesta_id, "publica", True)
        except Exception as e:
            print(f"Error al publicar la encuesta: {str(e)}")
            return False

    def add_question(self, encuesta_id, question_data):
        try:
            # Actualizar el documento de la encuesta para agregar la pregunta
            result = self.collection.update_one(
                {"id_encuesta": encuesta_id}, {"$push": {"preguntas": question_data}}
            )

            # Verificar si la actualización fue exitosa
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al agregar la pregunta: {str(e)}")
            return False

    def get_questions(self, encuesta_id):
        try:
            pregunta = self.get_encuesta_by_id(encuesta_id).get("preguntas")
            return pregunta
        except Exception as e:
            print(f"Error al obtener las preguntas: {str(e)}")
            return []

    def update_question(self, encuesta_id, question_id, updated_question_data):
        try:
            # Convertir el question_id a un índice entero
            question_index = int(question_id) - 1

            # Actualizar el documento de la encuesta para modificar la pregunta
            result = self.collection.update_one(
                {"id_encuesta": encuesta_id},
                {"$set": {f"preguntas.{question_index}": updated_question_data}},
            )

            # Verificar si la actualización fue exitosa
            return result.modified_count > 0
        except Exception as e:
            print(f"Error al actualizar la pregunta: {str(e)}")
            return False

    def delete_question(self, encuesta_id, question_id):
        try:
            # Convertir el question_id a un índice entero
            question_index = question_id - 1

            # Eliminar la pregunta del documento de la encuesta en la posición indicada
            result = self.collection.update_one(
                {"id_encuesta": encuesta_id},
                {"$unset": {f"preguntas.{question_index}": ""}},
            )

            # Verificar si la eliminación fue exitosa
            if result.modified_count > 0:
                # Eliminar los elementos nulos del arreglo de preguntas
                self.collection.update_one(
                    {"id_encuesta": encuesta_id}, {"$pull": {"preguntas": None}}
                )
                return True
            else:
                return False
        except Exception as e:
            print(f"Error al eliminar la pregunta: {str(e)}")
            return False
