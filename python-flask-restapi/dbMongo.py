# from pymongo import MongoClient


# Clase para interactuar con la base de datos MongoDB
class MongoDatabase:
    def __init__(self, mongoClient):
        self.client = mongoClient
        self.database = self.client["EncuestasDB"]
        self.collection = self.database["encuestas"]
        self.responsesCollect = self.database["respuestas"]

    # ------------------------------------------------------- FUNCIONES AUXILIARES -------------------------------------------------------
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

    # ------------------------------------------------------- SECCION DE ENCUESTAS -------------------------------------------------------
    def insert_encuesta(self, encuesta_data):
        # Convertir ObjectId a una representación serializable si es necesario
        self._convert_object_ids(encuesta_data)
        self.collection.insert_one(encuesta_data)

    def get_encuestas(self):
        encuestas = list(self.collection.find({"publica": "True"}))
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
        else:
            return False

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

    def publish_encuesta(self, encuesta_id):
        try:
            # Llamar a update_encuesta_key para establecer publica en True
            return self.update_encuesta_key(encuesta_id, "publica", True)
        except Exception as e:
            print(f"Error al publicar la encuesta: {str(e)}")
            return False

    # ------------------------------------------------------- SECCION DE PREGUNTAS -------------------------------------------------------
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

    # ------------------------------------------------------- SECCION DE RESPUESTAS A ENCUESTAS -------------------------------------------------------

    def submit_response(self, encuesta_id, usuario_id, response_data):
        try:
            response = {
                "encuesta_id": encuesta_id,
                "usuario_id": usuario_id,
                "respuestas": response_data,
            }
            if self.responsesCollect.insert_one(response):
                return True
            else:
                return False
        except Exception as e:
            print(f"Error al guardar la respuesta: {str(e)}")
            return False

    def get_responses(self, encuesta_id):
        try:
            responses = self.responsesCollect.find({"encuesta_id": encuesta_id})

            all_responses = []
            for response in responses:
                respuestas = response.get("respuestas", [])
                for respuesta in respuestas:
                    pregunta_respuesta = {
                        "encuesta_id": encuesta_id,
                        "id_usuario": response.get("usuario_id", ""),
                        "texto_pregunta": respuesta.get("texto_pregunta", ""),
                        "respuesta": respuesta.get("respuesta", ""),
                    }
                    all_responses.append(pregunta_respuesta)

            return all_responses
        except Exception as e:
            print(f"Error al obtener las respuestas: {str(e)}")
            return None

    # -------------------------------------------------------------- ANALISIS DE RESPUESTAS --------------------------------------------------------------
    def generate_analysis(self, encuesta_id):
        try:
            # Obtener todas las respuestas para la encuesta especificada
            respuestas = list(self.responsesCollect.find({"encuesta_id": encuesta_id}))

            # Inicializar un diccionario para almacenar el análisis
            analysis = {}

            # Procesar cada respuesta para generar el análisis
            for respuesta in respuestas:
                preguntas = respuesta.get("respuestas", [])

                for pregunta in preguntas:
                    texto_pregunta = pregunta.get("texto_pregunta")
                    respuesta_pregunta = pregunta.get("respuesta")

                    # Verificar si la pregunta ya existe en el análisis
                    if texto_pregunta in analysis:
                        # Incrementar el contador de la respuesta existente
                        if respuesta_pregunta in analysis[texto_pregunta]:
                            analysis[texto_pregunta][respuesta_pregunta] += 1
                        else:
                            analysis[texto_pregunta][respuesta_pregunta] = 1
                    else:
                        # Agregar la pregunta al análisis y establecer el contador de la respuesta
                        analysis[texto_pregunta] = {respuesta_pregunta: 1}

            return True, analysis
        except Exception as e:
            print(f"Error al generar el análisis: {str(e)}")
            return False, None
