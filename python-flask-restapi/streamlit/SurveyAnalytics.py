import os
import time
import streamlit as st
from pyspark.sql.types import (
    StructType, StructField, StringType, ArrayType, MapType
)
from pyspark.sql.functions import explode, col
from pymongo import MongoClient
from pyspark.sql import SparkSession
from neo4j import GraphDatabase
from pyvis.network import Network

# def create_nodes_and_relationships(driver, data_encuestas, data_respuestas):
#     def create_encuesta(tx, id_encuesta, titulo_encuesta):
#         query = """
#         MERGE (e:Encuesta {id_encuesta: $id_encuesta})
#         ON CREATE SET e.titulo_encuesta = $titulo_encuesta
#         """
#         tx.run(query, id_encuesta=id_encuesta, titulo_encuesta=titulo_encuesta)

#     def create_pregunta(tx, id_encuesta, texto_pregunta, tipo_pregunta):
#         query = """
#         MERGE (p:Pregunta {texto_pregunta: $texto_pregunta, tipo_pregunta: $tipo_pregunta})
#         WITH p
#         MATCH (e:Encuesta {id_encuesta: $id_encuesta})
#         MERGE (e)-[:TIENE_PREGUNTA]->(p)
#         """
#         tx.run(query, id_encuesta=id_encuesta, texto_pregunta=texto_pregunta, tipo_pregunta=tipo_pregunta)

#     def create_usuario(tx, usuario_id):
#         query = """
#         MERGE (u:Usuario {usuario_id: $usuario_id})
#         """
#         tx.run(query, usuario_id=usuario_id)

#     def create_respuesta(tx, usuario_id, texto_pregunta, respuesta):
#         query = """
#         MERGE (r:Respuesta {texto_pregunta: $texto_pregunta, respuesta: $respuesta})
#         WITH r
#         MATCH (u:Usuario {usuario_id: $usuario_id})
#         MERGE (u)-[:RESPONDIO]->(r)
#         WITH r
#         MATCH (p:Pregunta {texto_pregunta: $texto_pregunta})
#         MERGE (r)-[:ES_PREGUNTA_DE]->(p)
#         """
#         tx.run(query, usuario_id=usuario_id, texto_pregunta=texto_pregunta, respuesta=respuesta)

#     with driver.session() as session:
#         for encuesta in data_encuestas:
#             id_encuesta = encuesta["id_encuesta"]
#             titulo_encuesta = encuesta["titulo_encuesta"]
#             session.write_transaction(create_encuesta, id_encuesta, titulo_encuesta)

#             for pregunta in encuesta["preguntas"]:
#                 texto_pregunta = pregunta["texto_pregunta"]
#                 tipo_pregunta = pregunta["tipo_pregunta"]
#                 session.write_transaction(create_pregunta, id_encuesta, texto_pregunta, tipo_pregunta)

#         for respuesta_doc in data_respuestas:
#             usuario_id = respuesta_doc["usuario_id"]
#             id_encuesta = respuesta_doc["encuesta_id"]
#             session.write_transaction(create_usuario, usuario_id)

#             for respuesta in respuesta_doc["respuestas"]:
#                 texto_pregunta = respuesta["texto_pregunta"]
#                 respuesta_value = respuesta["respuesta"]
#                 session.write_transaction(create_respuesta, usuario_id, texto_pregunta, respuesta_value)

def load_encuestas_to_neo4j(encuestas_collection, driver):
    with driver.session() as session:
        encuestas_docs = list(encuestas_collection.find())

        for encuesta in encuestas_docs:
            id_encuesta = encuesta['id_encuesta']
            titulo_encuesta = encuesta['titulo_encuesta']

            # Crear o encontrar el nodo de Encuesta
            session.run(
                """
                MERGE (e:Encuesta {id: $id_encuesta})
                ON CREATE SET e.titulo_encuesta = $titulo_encuesta
                """,
                id_encuesta=id_encuesta,
                titulo_encuesta=titulo_encuesta
            )

            # Iterar sobre las preguntas de la encuesta
            for pregunta in encuesta.get('preguntas', []):
                texto_pregunta = pregunta['texto_pregunta']
                tipo_pregunta = pregunta['tipo_pregunta']

                # Crear o encontrar el nodo de Pregunta
                session.run(
                    """
                    MERGE (p:Pregunta {texto_pregunta: $texto_pregunta, tipo_pregunta: $tipo_pregunta})
                    WITH p
                    MATCH (e:Encuesta {id: $id_encuesta})
                    MERGE (e)-[:TIENE_PREGUNTA]->(p)
                    """,
                    id_encuesta=id_encuesta,
                    texto_pregunta=texto_pregunta,
                    tipo_pregunta=tipo_pregunta
                )

def load_responses_to_neo4j(respuestas_collection, driver):
    with driver.session() as session:
        respuestas_docs = list(respuestas_collection.find())
        
        for doc in respuestas_docs:
            encuesta_id = doc['encuesta_id']
            usuario_id = doc['usuario_id']
            
            # Crear o encontrar el nodo de Usuario
            session.run(
                """
                MERGE (u:Usuario {id: $usuario_id})
                """,
                usuario_id=usuario_id
            )
            
            # Crear o encontrar el nodo de Encuesta
            session.run(
                """
                MERGE (e:Encuesta {id: $encuesta_id})
                """,
                encuesta_id=encuesta_id
            )
            
            # Crear la relación entre Usuario y Encuesta
            session.run(
                """
                MATCH (u:Usuario {id: $usuario_id}), (e:Encuesta {id: $encuesta_id})
                MERGE (u)-[:RESPONDE]->(e)
                """,
                usuario_id=usuario_id,
                encuesta_id=encuesta_id
            )
            
            for respuesta in doc['respuestas']:
                pregunta_num = respuesta['pregunta_num']
                texto_pregunta = respuesta['texto_pregunta']
                texto_respuesta = respuesta['respuesta']
                
                # Crear o encontrar el nodo de Pregunta
                session.run(
                    """
                    MERGE (p:Pregunta {texto_pregunta: $texto_pregunta})
                    """,
                    texto_pregunta=texto_pregunta
                )
                
                # Crear el nodo de Respuesta y relacionarlo con Pregunta
                session.run(
                    """
                    CREATE (r:Respuesta {id: $respuesta_id, texto: $texto_respuesta})
                    WITH r
                    MATCH (p:Pregunta {texto_pregunta: $texto_pregunta})
                    MERGE (r)-[:RESPUESTA_A]->(p)
                    """,
                    respuesta_id=f"{usuario_id}{encuesta_id}{pregunta_num}",
                    texto_respuesta=texto_respuesta,
                    texto_pregunta=texto_pregunta
                )
                
                # Relacionar la Respuesta con el Usuario
                session.run(
                    """
                    MATCH (u:Usuario {id: $usuario_id}), (r:Respuesta {id: $respuesta_id})
                    MERGE (u)-[:TIENE_RESPUESTA]->(r)
                    """,
                    usuario_id=usuario_id,
                    respuesta_id=f"{usuario_id}{encuesta_id}{pregunta_num}"
                )
                
                # Relacionar la Respuesta con la Encuesta
                session.run(
                    """
                    MATCH (e:Encuesta {id: $encuesta_id}), (r:Respuesta {id: $respuesta_id})
                    MERGE (e)-[:CONTIENE_RESPUESTA]->(r)
                    """,
                    encuesta_id=encuesta_id,
                    respuesta_id=f"{usuario_id}{encuesta_id}{pregunta_num}"
                )

def createDF(spark, collection):
    documents = list(collection.find())
    if not documents:
        print("No hay documentos en la colección.")
        return spark.createDataFrame([], schema=StructType([]))

    for doc in documents:
        doc.pop("_id", None)

    schema = StructType()
    for key in documents[0].keys():
        if isinstance(documents[0][key], list):
            schema.add(
                StructField(key, ArrayType(MapType(StringType(), StringType())), True)
            )
        else:
            schema.add(StructField(key, StringType(), True))

    spark_df = spark.createDataFrame(documents, schema=schema)
    return spark_df

def formatDF(encuestasDF, respuestasDF):
    try:
        encuestasDF = encuestasDF.withColumn("preguntas", explode("preguntas"))
        encuestasDF = encuestasDF.select(
            "*",
            col("preguntas")["texto_pregunta"].alias("texto_pregunta"),
            col("preguntas")["posibles_respuestas"].alias("posibles_respuestas"),
            col("preguntas")["tipo_pregunta"].alias("tipo_pregunta"),
        )
        encuestasDF = encuestasDF.drop("preguntas")

        respuestasDF = respuestasDF.withColumn("respuestas", explode("respuestas"))
        respuestasDF = respuestasDF.select(
            "*",
            col("respuestas")["respuesta"].alias("respuesta"),
            col("respuestas")["texto_pregunta"].alias("texto_pregunta"),
            col("respuestas")["pregunta_num"].alias("pregunta_num"),
        )
        respuestasDF = respuestasDF.drop("respuestas")
    except Exception as e:
        st.write(f"Error while flattening DF: {e}")
    return encuestasDF, respuestasDF

def showDF(encuestasDF, respuestasDF):
    try:
        st.write("Data from MongoDB (Encuestas):")
        st.write(f"Number of rows in encuestasDF: {encuestasDF.count()}")
        if encuestasDF.count() < 1000:
            st.dataframe(encuestasDF.limit(100).toPandas())
        else:
            st.write("DataFrame is too large to display with Pandas.")
    except Exception as e:
        st.write(f"Error while converting encuestasDF to Pandas: {e}")

    try:
        st.write("Data from MongoDB (Respuestas):")
        st.write(f"Number of rows in respuestasDF: {respuestasDF.count()}")
        if respuestasDF.count() < 1000:
            st.dataframe(respuestasDF.limit(100).toPandas())
        else:
            st.write("DataFrame is too large to display with Pandas.")
    except Exception as e:
        st.write(f"Error while converting respuestasDF to Pandas: {e}")

def visualize_graph(driver):
    net = Network(notebook=True)
    
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """
    
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            node1 = record['n']
            node2 = record['m']
            relationship = record['r']
            node1_id = node1.get('id', '')
            node2_id = node2.get('id', '')
            net.add_node(node1_id, label=node1.get('texto', node1_id))
            net.add_node(node2_id, label=node2.get('texto', node2_id))
            net.add_edge(node1_id, node2_id, label=relationship.type)

    net.show('graph.html')
    return 'graph.html'

def main():
    st.title("Survey Analytics")

    spark = (
        SparkSession.builder.appName("SurveyAnalytics")
        .master("spark://spark:7077")
        .config("spark.executor.memory", "4g")
        .config("spark.executor.cores", "2")
        .config("spark.driver.memory", "2g")
        .config("spark.network.timeout", "600s")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )

    mongo_uri = "mongodb://root:password@mongo:27017/?authSource=admin"
    client = MongoClient(mongo_uri)
    mongoDB = client["EncuestasDB"]
    encuestasCollection = mongoDB["encuestas"]
    respuestasCollection = mongoDB["respuestas"]

    neo4j_uri = "bolt://neo4j:7687"
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")

    st.write("Neo4j URI:", neo4j_uri, "Neo4j User:", neo4j_user, "Neo4j Password:", neo4j_password)  

    max_retries = 5
    for i in range(max_retries):
        try:
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            st.write("Connected to Neo4j.")
            break
        except Exception as e:
            st.write(f"Error connecting to Neo4j (attempt {i + 1}/{max_retries}): {e}")
            time.sleep(5)
    else:
        st.write("Failed to connect to Neo4j after several attempts.")
        return

    st.write("Neo4j and Spark initialized.")

    load_encuestas_to_neo4j(encuestasCollection, driver)
    load_responses_to_neo4j(respuestasCollection, driver)

    st.write("Nodes and relationships created in Neo4j.")

     # Visualizar el gráfico
    graph_html_path = visualize_graph(driver)
    st.components.v1.html(open(graph_html_path, 'r').read(), height=800)

if __name__ == "__main__":
    main()