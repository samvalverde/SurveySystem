import os
import time
import streamlit as st
from pyspark.sql import SparkSession
from neo4j import GraphDatabase
from pyvis.network import Network
import plotly.express as px
import pandas as pd

def create_nodes_and_relationships(driver, data_encuestas, data_respuestas):
    def create_encuesta(tx, id_encuesta, titulo_encuesta):
        query = """
        MERGE (e:Encuesta {id_encuesta: $id_encuesta})
        ON CREATE SET e.titulo_encuesta = $titulo_encuesta
        """
        tx.run(query, id_encuesta=id_encuesta, titulo_encuesta=titulo_encuesta)

    def create_pregunta(tx, id_encuesta, texto_pregunta, tipo_pregunta):
        query = """
        MERGE (p:Pregunta {texto_pregunta: $texto_pregunta, tipo_pregunta: $tipo_pregunta})
        WITH p
        MATCH (e:Encuesta {id_encuesta: $id_encuesta})
        MERGE (e)-[:TIENE_PREGUNTA]->(p)
        """
        tx.run(query, id_encuesta=id_encuesta, texto_pregunta=texto_pregunta, tipo_pregunta=tipo_pregunta)

    def create_usuario(tx, usuario_id):
        query = """
        MERGE (u:Usuario {usuario_id: $usuario_id})
        """
        tx.run(query, usuario_id=usuario_id)

    def create_respuesta(tx, usuario_id, texto_pregunta, respuesta):
        query = """
        MERGE (r:Respuesta {texto_pregunta: $texto_pregunta, respuesta: $respuesta})
        WITH r
        MATCH (u:Usuario {usuario_id: $usuario_id})
        MERGE (u)-[:RESPONDIO]->(r)
        WITH r
        MATCH (p:Pregunta {texto_pregunta: $texto_pregunta})
        MERGE (r)-[:ES_PREGUNTA_DE]->(p)
        """
        tx.run(query, usuario_id=usuario_id, texto_pregunta=texto_pregunta, respuesta=respuesta)

    with driver.session() as session:
        for encuesta in data_encuestas:
            id_encuesta = encuesta["id_encuesta"]
            titulo_encuesta = encuesta["titulo_encuesta"]
            session.write_transaction(create_encuesta, id_encuesta, titulo_encuesta)

            for pregunta in encuesta["preguntas"]:
                texto_pregunta = pregunta["texto_pregunta"]
                tipo_pregunta = pregunta["tipo_pregunta"]
                session.write_transaction(create_pregunta, id_encuesta, texto_pregunta, tipo_pregunta)

        for respuesta_doc in data_respuestas:
            usuario_id = respuesta_doc["usuario_id"]
            session.write_transaction(create_usuario, usuario_id)

            for respuesta in respuesta_doc["respuestas"]:
                texto_pregunta = respuesta["texto_pregunta"]
                respuesta_value = respuesta["respuesta"]
                session.write_transaction(create_respuesta, usuario_id, texto_pregunta, respuesta_value)

def draw_network_graph(data_encuestas, data_respuestas):
    net = Network(height='750px', width='100%', directed=True)
    
    for encuesta in data_encuestas:
        id_encuesta = encuesta['id_encuesta']
        titulo_encuesta = encuesta['titulo_encuesta']
        net.add_node(id_encuesta, label=titulo_encuesta, title=titulo_encuesta, shape='box')

        for pregunta in encuesta['preguntas']:
            texto_pregunta = pregunta['texto_pregunta']
            tipo_pregunta = pregunta['tipo_pregunta']
            net.add_node(texto_pregunta, label=texto_pregunta, title=tipo_pregunta, shape='ellipse')
            net.add_edge(id_encuesta, texto_pregunta, title='TIENE_PREGUNTA')

    for respuesta_doc in data_respuestas:
        usuario_id = respuesta_doc['usuario_id']
        net.add_node(usuario_id, label=f'Usuario {usuario_id}', shape='dot')

        for respuesta in respuesta_doc['respuestas']:
            texto_pregunta = respuesta['texto_pregunta']
            respuesta_value = respuesta['respuesta']
            respuesta_node = f'{usuario_id}_{texto_pregunta}_{respuesta_value}'
            net.add_node(respuesta_node, label=respuesta_value, shape='diamond')
            net.add_edge(usuario_id, respuesta_node, title='RESPONDIO')
            net.add_edge(respuesta_node, texto_pregunta, title='ES_PREGUNTA_DE')

    return net

def main():
    st.title("Survey Analytics")

    # Initialize Spark
    spark = None
    for attempt in range(5):  # Retry up to 5 times
        try:
            spark = (
                SparkSession.builder.appName("SurveyAnalytics")
                .master("spark://spark:7077")
                .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.0.0")
                .config("spark.mongodb.input.uri", "mongodb://mongo:27017/EncuestasDB")
                .config("spark.mongodb.output.uri", "mongodb://mongo:27017/EncuestasDB")
                .config("spark.mongodb.input.database", "EncuestasDB")
                .config("spark.mongodb.output.database", "EncuestasDB")
                .getOrCreate()
            )
            break
        except Exception as e:
            st.error(f"Failed to initialize Spark (attempt {attempt+1}/5): {e}")
            time.sleep(5)

    if spark is None:
        st.error("Could not initialize Spark. Exiting.")
        return

    # Load data from MongoDB
    df_encuestas = spark.read.format("mongo").option("collection", "encuestas").load()
    df_respuestas = spark.read.format("mongo").option("collection", "respuestas").load()
    data_encuestas = df_encuestas.collect()
    data_respuestas = df_respuestas.collect()

    # Convert to dictionary for easier processing
    data_encuestas = [row.asDict() for row in data_encuestas]
    data_respuestas = [row.asDict() for row in data_respuestas]

    # Display the data in Streamlit
    st.write("Data from MongoDB (Encuestas):")
    st.dataframe(df_encuestas.toPandas())
    st.write("Data from MongoDB (Respuestas):")
    st.dataframe(df_respuestas.toPandas())

    # Initialize Neo4j
    neo4j_uri = "bolt://neo4j:7687"
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
    driver = None
    for attempt in range(5):  # Retry up to 5 times
        try:
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            break
        except Exception as e:
            st.error(f"Failed to connect to Neo4j (attempt {attempt+1}/5): {e}")
            time.sleep(5)

    if driver is None:
        st.error("Could not connect to Neo4j. Exiting.")
        return

    st.write("Neo4j and Spark initialized.")

    # Create nodes and relationships in Neo4j
    create_nodes_and_relationships(driver, data_encuestas, data_respuestas)

    st.write("Nodes and relationships created in Neo4j.")

    # Draw the network graph
    net = draw_network_graph(data_encuestas, data_respuestas)
    net.show('network.html')
    with open('network.html', 'r', encoding='utf-8') as f:
        html = f.read()
    st.components.v1.html(html, height=750)

if __name__ == "__main__":
    main()
