import os
import streamlit as st
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
    ArrayType,
    MapType,
)
from pyspark.sql.functions import explode, col
from pymongo import MongoClient
import pandas as pd
from pyspark.sql import SparkSession
from neo4j import GraphDatabase


def createDF(spark, collection):
    # Obtener todos los documentos de la colección
    documents = list(collection.find())

    # Si no hay documentos, retornar un DataFrame vacío
    if not documents:
        print("No hay documentos en la colección.")
        return spark.createDataFrame([], schema=StructType([]))

    # Eliminar el campo _id de cada documento
    for doc in documents:
        doc.pop("_id", None)

    # Crear el esquema de Spark basado en los documentos
    schema = StructType()
    for key in documents[0].keys():
        if isinstance(documents[0][key], list):
            schema.add(
                StructField(key, ArrayType(MapType(StringType(), StringType())), True)
            )
        else:
            schema.add(StructField(key, StringType(), True))

    # Crear un DataFrame de Spark directamente desde los documentos
    spark_df = spark.createDataFrame(documents, schema=schema)

    return spark_df


def formatDF(encuestasDF, respuestasDF):
    try:
        # Flatten the preguntas column for encuestasDF
        encuestasDF = encuestasDF.withColumn("preguntas", explode("preguntas"))
        encuestasDF = encuestasDF.select(
            "*",
            col("preguntas")["texto_pregunta"].alias("texto_pregunta"),
            col("preguntas")["posibles_respuestas"].alias("posibles_respuestas"),
            col("preguntas")["tipo_pregunta"].alias("tipo_pregunta"),
        )
        encuestasDF = encuestasDF.drop("preguntas")
        # Flatten the respuestas column for respuestasDF
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
    return [encuestasDF, respuestasDF]


def showDF(encuestasDF, respuestasDF):
    try:
        st.write("Data from MongoDB (Encuestas):")
        st.write(f"Number of rows in encuestasDF: {encuestasDF.count()}")
        if encuestasDF.count() < 1000:
            st.dataframe(
                encuestasDF.limit(100).toPandas()
            )  # Limitar el número de filas a convertir a Pandas
        else:
            st.write("DataFrame is too large to display with Pandas.")
    except Exception as e:
        st.write(f"Error while converting encuestasDF to Pandas: {e}")

    try:
        st.write("Data from MongoDB (Respuestas):")
        st.write(f"Number of rows in respuestasDF: {respuestasDF.count()}")
        if respuestasDF.count() < 1000:
            st.dataframe(
                respuestasDF.limit(100).toPandas()
            )  # Limitar el número de filas a convertir a Pandas
        else:
            st.write("DataFrame is too large to display with Pandas.")
    except Exception as e:
        st.write(f"Error while converting respuestasDF to Pandas: {e}")


def main():
    st.title("Survey Analytics")

    # Initialize Spark
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

    # Creates both dataframes for encuestasCollection and respuestasCollection
    encuestasDF = createDF(spark, encuestasCollection)
    respuestasDF = createDF(spark, respuestasCollection)
    formateados = formatDF(encuestasDF, respuestasDF)
    encuestasDF = formateados[0]
    respuestasDF = formateados[1]
    # Shows both dataframes for encuestasCollection and respuestasCollection using streamlit
    showDF(encuestasDF, respuestasDF)

    # Initialize Neo4j
    neo4j_uri = "bolt://neo4j:7687"
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    st.write("Neo4j and Spark initialized.")

    st.write("Nodes and relationships created in Neo4j.")


if __name__ == "__main__":
    main()
