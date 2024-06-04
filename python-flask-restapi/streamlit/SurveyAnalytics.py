# SurveyAnalytics.py

import streamlit as st
from pyspark.sql import SparkSession
from neo4j import GraphDatabase


def main():
    st.title("Survey Analytics")

    # Initialize Spark
    # spark = SparkSession.builder.appName("SurveyAnalytics").getOrCreate()
    spark = (
        SparkSession.builder.appName("SurveyAnalytics")
        .master("spark://spark:7077")
        .getOrCreate()
    )
    # Initialize Neo4j
    neo4j_uri = "bolt://neo4j:7687"
    neo4j_user = "neo4j"
    neo4j_password = "password"
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    st.write("Neo4j and Spark initialized.")

    # Example query for Neo4j
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 5")
        nodes = result.data()
        st.write("Nodes in Neo4j:", nodes)

    # Example DataFrame for Spark
    data = [("Alice", 1), ("Bob", 2), ("Cathy", 3)]
    df = spark.createDataFrame(data, ["Name", "Value"])
    st.write("Example DataFrame using Spark:")
    st.write(df.show())


if __name__ == "__main__":
    main()
