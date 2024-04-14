FROM python:3.11

# Instalar dependencias y configurar el directorio de trabajo
WORKDIR /opt/app
COPY . .
RUN pip install poetry
RUN poetry install

# Exponer el puerto 5000 donde Flask escuchará las conexiones
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["poetry", "run", "python3", "-m", "flask", "run", "--host=0.0.0.0"]
