#Usar una imagen base oficial de Python
FROM python:3.11

#Establecer el directorio de trabajo en el contenedor
WORKDIR /app

#Copiar el archivo de requisitos
COPY requirements.txt ./

#Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

#Instalar PySpark
RUN pip install pyspark

#Instalar dependencias plotly
RUN pip install matplotlib seaborn plotly

#Instalar Java 17
RUN apt-get update && apt-get install -y openjdk-17-jre

ENV JAVA_HOME /usr/lib/jvm/java-17-openjdk-amd64


#Copiar el contenido de la aplicación en el contenedor
COPY . .

#Exponer el puerto que usará la aplicación Streamlit
EXPOSE 8501

#Comando para ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "SurveyAnalytics.py", "--server.port=8501", "--server.address=0.0.0.0"]