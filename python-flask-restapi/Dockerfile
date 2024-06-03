# Usa la imagen base de Python 3.11
FROM python:3.11

# Variables de entorno para la base de datos PostgreSQL
ENV DB_HOST_POSTGRES=db
ENV DB_PORT_POSTGRES=5432
ENV DB_NAME_POSTGRES=tasks
ENV DB_USER_POSTGRES=postgres
ENV DB_PASSWORD_POSTGRES=mysecretpassword

# Variables de entorno para la base de datos MongoDB
ENV DB_HOST_MONGO=mongo
ENV DB_PORT_MONGO=27017
ENV DB_USER_MONGO=root
ENV DB_PASSWORD_MONGO=password

# Variables de entorno para redis
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_DB=0

# Variables de entorno para kafka
#ENV KAFKA_BROKER_URL=localhost:9092
#ENV KAFKA_LISTENERS=PLAINTEXT://localhost:9092
#ENV KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
# Establece el directorio de trabajo en /opt/app
WORKDIR /opt/app

# Copia los archivos de la aplicación al contenedor
COPY . .

# Instala Poetry y las dependencias del proyecto
RUN pip install poetry && poetry install

# Expone el puerto 5000 para la aplicación Flask
EXPOSE 5000

# Comando para iniciar la aplicación Flask
CMD ["poetry", "run", "python", "-m", "flask", "run", "--host=0.0.0.0"]
