import os
import streamlit as st
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    ArrayType,
    MapType,
)
from pyspark.sql.functions import explode, col
from pymongo import MongoClient
import pandas as pd
from pyspark.sql import SparkSession
from neo4j import GraphDatabase
from streamlit_autorefresh import st_autorefresh
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px


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

# Initialize Neo4j
neo4j_uri = "bolt://neo4j:7687"
driver = GraphDatabase.driver(neo4j_uri, auth=("neo4j", "password"))


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


def load_responses_to_neo4j(respuestas_collection, driver):
    with driver.session() as session:
        respuestas_docs = list(respuestas_collection.find())

        for doc in respuestas_docs:
            encuesta_id = doc["encuesta_id"]
            usuario_id = doc["usuario_id"]

            session.run(
                """
                MERGE (u:Usuario {id: $usuario_id})
                ON CREATE SET u.tipo = 'Usuario'
                """,
                usuario_id=usuario_id,
            )

            session.run(
                """
                MERGE (e:Encuesta {id: $encuesta_id})
                ON CREATE SET e.tipo = 'Encuesta'
                """,
                encuesta_id=encuesta_id,
            )

            session.run(
                """
                MATCH (u:Usuario {id: $usuario_id}), (e:Encuesta {id: $encuesta_id})
                MERGE (u)-[:RESPONDE]->(e)
                """,
                usuario_id=usuario_id,
                encuesta_id=encuesta_id,
            )

            for respuesta in doc["respuestas"]:
                pregunta_num = respuesta["pregunta_num"]
                texto_pregunta = respuesta["texto_pregunta"]
                texto_respuesta = respuesta["respuesta"]

                session.run(
                    """
                    MERGE (p:Pregunta {id: $pregunta_num, texto: $texto_pregunta})
                    ON CREATE SET p.tipo = 'Pregunta'
                    """,
                    pregunta_num=pregunta_num,
                    texto_pregunta=texto_pregunta,
                )

                session.run(
                    """
                    CREATE (r:Respuesta {id: $respuesta_id, texto: $texto_respuesta})
                    SET r.tipo = 'Respuesta'
                    MERGE (p:Pregunta {id: $pregunta_num, texto: $texto_pregunta})
                    MERGE (r)-[:RESPUESTA_A]->(p)
                    """,
                    respuesta_id=f"{usuario_id}_{encuesta_id}_{pregunta_num}",
                    texto_respuesta=texto_respuesta,
                    pregunta_num=pregunta_num,
                    texto_pregunta=texto_pregunta,
                )

                session.run(
                    """
                    MATCH (u:Usuario {id: $usuario_id}), (r:Respuesta {id: $respuesta_id})
                    MERGE (u)-[:TIENE_RESPUESTA]->(r)
                    """,
                    usuario_id=usuario_id,
                    respuesta_id=f"{usuario_id}_{encuesta_id}_{pregunta_num}",
                )

                session.run(
                    """
                    MATCH (e:Encuesta {id: $encuesta_id}), (r:Respuesta {id: $respuesta_id})
                    MERGE (e)-[:CONTIENE_RESPUESTA]->(r)
                    """,
                    encuesta_id=encuesta_id,
                    respuesta_id=f"{usuario_id}_{encuesta_id}_{pregunta_num}",
                )


def visualize_graph(driver):
    G = nx.Graph()

    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m
    """

    with driver.session() as session:
        result = session.run(query)
        for record in result:
            node1 = record["n"]
            node2 = record["m"]
            relationship = record["r"]
            node1_id = f"{list(node1.labels)[0]}_{node1.get('id', '')}"
            node2_id = f"{list(node2.labels)[0]}_{node2.get('id', '')}"
            node1_label = (
                f"{list(node1.labels)[0]}: {node1.get('texto', node1.get('id', ''))}"
            )
            node2_label = (
                f"{list(node2.labels)[0]}: {node2.get('texto', node2.get('id', ''))}"
            )
            G.add_node(node1_id, label=node1_label)
            G.add_node(node2_id, label=node2_label)
            G.add_edge(node1_id, node2_id, label=relationship.type)

    pos = nx.spring_layout(G)

    edge_trace = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=0.5, color="#888"),
                hoverinfo="none",
                mode="lines",
            )
        )

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers+text",
        textposition="top center",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right",
            ),
        ),
    )

    for node in G.nodes():
        x, y = pos[node]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
        node_trace["text"] += tuple([G.nodes[node]["label"]])

    fig = go.Figure(
        data=edge_trace + [node_trace],
        layout=go.Layout(
            title="Grafo de relaciones generales en respuestas de encuestas",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
        ),
    )
    return fig


def generate_similarity_graph(respuestas_pd):
    G = nx.Graph()

    # Crear un conjunto de usuarios y sus respuestas
    usuario_respuestas = {}
    for _, row in respuestas_pd.iterrows():
        usuario_id = f"Usuario_{row['usuario_id']}"
        respuesta_id = f"Encuesta_{row['encuesta_id']}_Pregunta_{row['pregunta_num']}_Respuesta_{row['respuesta']}"

        if usuario_id not in usuario_respuestas:
            usuario_respuestas[usuario_id] = set()
        usuario_respuestas[usuario_id].add(respuesta_id)

        # Añadir nodo de respuesta
        G.add_node(
            respuesta_id,
            label=f"Respuesta: {row['respuesta']}",
            title=f"Encuesta: {row['encuesta_id']}, Pregunta: {row['pregunta_num']}, Respuesta: {row['respuesta']}",
        )

    # Añadir nodos de usuarios y relaciones
    for usuario_id, respuestas in usuario_respuestas.items():
        G.add_node(
            usuario_id, label=usuario_id, title=f"Usuario: {usuario_id.split('_')[1]}"
        )
        for respuesta_id in respuestas:
            G.add_edge(usuario_id, respuesta_id, label="RESPONDE_A")

    # Añadir relaciones entre usuarios basadas en similitud de respuestas
    usuarios = list(usuario_respuestas.keys())
    for i in range(len(usuarios)):
        for j in range(i + 1, len(usuarios)):
            usuario1 = usuarios[i]
            usuario2 = usuarios[j]
            respuestas_comunes = usuario_respuestas[usuario1].intersection(
                usuario_respuestas[usuario2]
            )
            if respuestas_comunes:
                G.add_edge(usuario1, usuario2, label="SIMILAR_RESPUESTA")

    pos = nx.spring_layout(G)

    edge_trace = []
    for edge in G.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=0.5, color="#888"),
                hoverinfo="none",
                mode="lines",
            )
        )

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode="markers+text",
        textposition="top center",
        hoverinfo="text",
        marker=dict(
            showscale=True,
            colorscale="YlGnBu",
            size=10,
            colorbar=dict(
                thickness=15,
                title="Node Connections",
                xanchor="left",
                titleside="right",
            ),
        ),
    )

    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_trace["x"] += tuple([x])
        node_trace["y"] += tuple([y])
        node_trace["text"] += tuple([f"{node[1]['label']}: {node[1]['title']}"])

    fig = go.Figure(
        data=edge_trace + [node_trace],
        layout=go.Layout(
            title="SGrafo similitud de entre respuestas de usuarios",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=[
                dict(
                    text="",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
        ),
    )
    return fig


def generate_user_responses_chart(respuestas_pd):
    respuestas_por_usuario = (
        respuestas_pd.groupby("usuario_id").size().reset_index(name="counts")
    )
    fig_usuario = px.bar(
        respuestas_por_usuario,
        x="usuario_id",
        y="counts",
        title="Cantidad de respuestas por usuario",
    )
    return fig_usuario


def generate_survey_responses_chart(respuestas_pd):
    respuestas_por_encuesta = (
        respuestas_pd.groupby("encuesta_id").size().reset_index(name="counts")
    )
    fig_encuesta = px.bar(
        respuestas_por_encuesta,
        x="encuesta_id",
        y="counts",
        title="Cantidad de respuestas por encuesta",
    )
    return fig_encuesta


def generate_yes_no_chart(respuestas_pd, encuesta_id, pregunta_num):
    respuestas_especificas = respuestas_pd[
        (respuestas_pd["encuesta_id"] == encuesta_id)
        & (respuestas_pd["pregunta_num"] == pregunta_num)
    ]
    respuestas_si = respuestas_especificas[
        respuestas_especificas["respuesta"] == "Sí"
    ].shape[0]
    respuestas_no = respuestas_especificas[
        respuestas_especificas["respuesta"] == "No"
    ].shape[0]
    total_respuestas = respuestas_si + respuestas_no

    porcentaje_si = (
        (respuestas_si / total_respuestas) * 100 if total_respuestas > 0 else 0
    )
    porcentaje_no = (
        (respuestas_no / total_respuestas) * 100 if total_respuestas > 0 else 0
    )

    fig_pie = go.Figure(
        data=[
            go.Pie(
                labels=["Sí", "No"],
                values=[porcentaje_si, porcentaje_no],
                hole=0.3,
                marker=dict(colors=["blue", "red"]),
            )
        ]
    )
    fig_pie.update_layout(
        title_text=(
            respuestas_especificas.iloc[0]["texto_pregunta"]
            if not respuestas_especificas.empty
            else "Pregunta no encontrada"
        )
    )

    return fig_pie


def main():
    st.title("Survey Analytics")

    # Auto-refresco cada 60 segundos
    st_autorefresh(interval=60000, key="datarefresh")

    # Creates both dataframes for encuestasCollection and respuestasCollection
    encuestasDF = createDF(spark, encuestasCollection)
    respuestasDF = createDF(spark, respuestasCollection)
    formateados = formatDF(encuestasDF, respuestasDF)
    encuestasDF = formateados[0]
    respuestasDF = formateados[1]
    # Shows both dataframes for encuestasCollection and respuestasCollection using streamlit
    showDF(encuestasDF, respuestasDF)

    # Convertir respuestasDF a pandas
    respuestas_pd = respuestasDF.toPandas()

    # Generar y mostrar gráficos de barras y pie
    fig_usuario = generate_user_responses_chart(respuestas_pd)
    st.plotly_chart(fig_usuario)

    fig_encuesta = generate_survey_responses_chart(respuestas_pd)
    st.plotly_chart(fig_encuesta)

    encuesta_id = "1"  # ID de la encuesta a analizar
    pregunta_num = (
        "2"  # Número de la pregunta a analizar (si recomienda o no el srivicio)
    )
    fig_pie = generate_yes_no_chart(respuestas_pd, encuesta_id, pregunta_num)
    st.plotly_chart(fig_pie)

    # Cargar los datos de respuestas en Neo4j
    load_responses_to_neo4j(respuestasCollection, driver)

    # Visualizar el gráfico de las relaciones existentes en todas las respuestas
    fig = visualize_graph(driver)
    st.plotly_chart(fig)

    # Generar y mostrar el grafo de similitudes entre respuestas de usuarios
    fig_similarity = generate_similarity_graph(respuestas_pd)
    st.plotly_chart(fig_similarity)


if __name__ == "__main__":
    main()
