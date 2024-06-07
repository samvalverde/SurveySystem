import os
import streamlit as st
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, MapType
from pyspark.sql.functions import explode, col
from pymongo import MongoClient
from pyspark.sql import SparkSession
from neo4j import GraphDatabase
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


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
            id_encuesta = respuesta_doc["encuesta_id"]
            session.write_transaction(create_usuario, usuario_id)

            for respuesta in respuesta_doc["respuestas"]:
                texto_pregunta = respuesta["texto_pregunta"]
                respuesta_value = respuesta["respuesta"]
                session.write_transaction(create_respuesta, usuario_id, texto_pregunta, respuesta_value)

def createDF(spark, collection):
    documents = list(collection.find())
    if not documents:
        print("No hay documentos en la colección.")
        return spark.createDataFrame([], schema=StructType([]))

    for doc in documents:
        doc.pop('_id', None)

    schema = StructType()
    for key in documents[0].keys():
        if isinstance(documents[0][key], list):
            schema.add(StructField(key, ArrayType(MapType(StringType(), StringType())), True))
        else:
            schema.add(StructField(key, StringType(), True))

    spark_df = spark.createDataFrame(documents, schema=schema)
    return spark_df

def showDF(encuestasDF, respuestasDF):
    try:
        encuestasDF = encuestasDF.withColumn("preguntas", explode("preguntas"))
        encuestasDF = encuestasDF.select("*", col("preguntas")["texto_pregunta"].alias("texto_pregunta"),
                                               col("preguntas")["posibles_respuestas"].alias("posibles_respuestas"),
                                               col("preguntas")["tipo_pregunta"].alias("tipo_pregunta"))
        encuestasDF = encuestasDF.drop("preguntas")
        respuestasDF = respuestasDF.withColumn("respuestas", explode("respuestas"))
        respuestasDF = respuestasDF.select("*", col("respuestas")["respuesta"].alias("respuesta"),
                                               col("respuestas")["texto_pregunta"].alias("texto_pregunta"),
                                               col("respuestas")["pregunta_num"].alias("pregunta_num"))
        respuestasDF = respuestasDF.drop("respuestas")
    except Exception as e:
        st.write(f"Error while flattening DF: {e}")

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

def create_graphs(encuestasDF, respuestasDF):
    st.write("Graphs:")

    # Convert Spark DataFrames to Pandas DataFrames for easy plotting
    encuestas_pd = encuestasDF.toPandas()
    respuestas_pd = respuestasDF.toPandas()

    # Example Graph 1: Number of Questions per Survey
    st.write("Numero de Preguntas por Cuestionario")
    num_questions_per_survey = encuestas_pd.groupby('id_encuesta').size().reset_index(name='num_questions')
    fig1, ax1 = plt.subplots()
    sns.barplot(data=num_questions_per_survey, x='id_encuesta', y='num_questions', ax=ax1)
    st.pyplot(fig1)

    # Example Graph 2: Number of Responses per User
    st.write("Numero de Respuestas por Usuario")
    num_responses_per_user = respuestas_pd.groupby('usuario_id').size().reset_index(name='num_responses')
    fig2, ax2 = plt.subplots()
    sns.barplot(data=num_responses_per_user, x='usuario_id', y='num_responses', ax=ax2)
    st.pyplot(fig2)

    # Example Graph 3: Distribution of Response Types
    st.write("Distribucion de Tipos de Respuestas")
    response_types = respuestas_pd['respuesta'].value_counts().reset_index(name='count')
    fig3, ax3 = plt.subplots()
    sns.barplot(data=response_types, x='index', y='count', ax=ax3)
    ax3.set(xlabel='Response Type', ylabel='Count')
    st.pyplot(fig3)

    # Example Graph 4: Survey Titles Word Cloud (requires wordcloud library)
    from wordcloud import WordCloud
    st.write("Survey Titles Word Cloud")
    wordcloud = WordCloud(width=800, height=400).generate(' '.join(encuestas_pd['titulo_encuesta']))
    fig4, ax4 = plt.subplots()
    ax4.imshow(wordcloud, interpolation='bilinear')
    ax4.axis('off')
    st.pyplot(fig4)

    # Example Graph 5: Number of Questions by Question Type
    st.write("Numero de Preguntas por Tipo")
    num_questions_by_type = encuestas_pd.groupby('tipo_pregunta').size().reset_index(name='num_questions')
    fig5, ax5 = plt.subplots()
    sns.barplot(data=num_questions_by_type, x='tipo_pregunta', y='num_questions', ax=ax5)
    st.pyplot(fig5)

    # Example Graph 6: Responses by Question
    st.write("Respuestas por Pregunta")
    responses_by_question = respuestas_pd.groupby('texto_pregunta').size().reset_index(name='num_responses')
    fig6, ax6 = plt.subplots()
    sns.barplot(data=responses_by_question, x='texto_pregunta', y='num_responses', ax=ax6)
    plt.xticks(rotation=90)
    st.pyplot(fig6)


def main():
    st.title("Survey Analytics")

    spark = SparkSession.builder \
            .appName("SurveyAnalytics") \
            .master("spark://spark:7077") \
            .config("spark.executor.memory", "4g") \
            .config("spark.executor.cores", "2") \
            .config("spark.driver.memory", "2g") \
            .config("spark.network.timeout", "600s") \
            .config("spark.sql.shuffle.partitions", "2") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .getOrCreate()

    mongo_uri = "mongodb://root:password@mongo:27017/?authSource=admin"
    client = MongoClient(mongo_uri)
    mongoDB = client["EncuestasDB"]
    encuestasCollection = mongoDB["encuestas"]
    respuestasCollection = mongoDB["respuestas"]

    encuestasDF = createDF(spark, encuestasCollection)
    respuestasDF = createDF(spark, respuestasCollection)
    showDF(encuestasDF, respuestasDF)

    data_encuestas = encuestasDF.collect()
    data_respuestas = respuestasDF.collect()

    neo4j_uri = "bolt://neo4j:7687"
    neo4j_user = "neo4j"
    #os.getenv("NEO4J_USER")
    neo4j_password = "password"
    #os.getenv("NEO4J_PASSWORD")

    st.write(f"Neo4j User: {neo4j_user}")
    st.write(f"Neo4j Password: {neo4j_password}")

    # Hardcode credentials for testing
    # neo4j_user = "your_username"
    # neo4j_password = "your_password"

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    st.write("Neo4j and Spark initialized.")
    create_nodes_and_relationships(driver, data_encuestas, data_respuestas)
    st.write("Nodes and relationships created in Neo4j.")

    # Call the create_graphs function to display the graphs
    create_graphs(encuestasDF, respuestasDF)


if __name__ == "__main__":
    main()

