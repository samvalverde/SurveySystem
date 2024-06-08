# SurveySystem

El objetivo del proyecto SurveySystem es diseñar e implementar un sistema de encuestas de back-end utilizando tecnologías modernas como Docker, Docker Compose, MongoDB, PostgreSQL, Redis y RestAPI. Este sistema permite a los usuarios crear, publicar y gestionar encuestas con distintos tipos de preguntas, además de registrar y administrar listas de encuestados. Adicionalmente, el proyecto incorpora herramientas avanzadas para el manejo de mensajes en tiempo real, análisis de datos y edición colaborativa.
Estructura del Proyecto
Carpeta Principal: python-flask-restapi

Esta carpeta contiene los archivos esenciales para el funcionamiento del sistema. Dentro de ella se encuentra la implementación de la lógica del back-end utilizando Flask.
Archivo Clave: docker-compose.yml

Este archivo es fundamental para levantar el sistema. Define los servicios necesarios, incluyendo:

    Servicios: Especifica los contenedores que se utilizarán, sus imágenes correspondientes y cómo interactúan entre sí.
    Puertos: Configura los puertos de acceso para cada servicio.
    Volúmenes: Gestiona los volúmenes para persistencia de datos.
    Variables de Entorno: Define las variables necesarias para la configuración de los servicios.

Bases de Datos

    PostgreSQL: Utilizado para el almacenamiento de datos relacionales.
    MongoDB: Utilizado para datos no estructurados o semi-estructurados.
    Redis: Utilizado para almacenamiento en caché y gestión de sesiones.

Requisitos Previos

Para ejecutar el sistema, asegúrese de tener instalados los siguientes componentes:

    Docker Desktop: Herramienta para gestionar contenedores Docker.
    Docker Compose: Utilizado para definir y ejecutar aplicaciones multi-contenedor.

Instrucciones de Configuración

    Abrir Terminal: Navegue hasta la carpeta python-flask-restapi.

    Ejecutar Comando:
    docker-compose up --build

    Este comando levantará todos los servicios definidos en el archivo docker-compose.yml, configurando las bases de datos y otros componentes necesarios.

    Acceder a Endpoints: Una vez que todos los servicios estén corriendo, podrá utilizar las funciones del sistema a través de los endpoints definidos. Los detalles de estos endpoints están documentados en una colección de Postman que se puede acceder mediante el siguiente enlace:

    https://app.getpostman.com/join-team?invite_code=e59ba8eaca721167264e766626873c6d&target_code=1481d8da825688d73ee1892e8fb3eb87

Proceso de Autenticación

Para utilizar el sistema, siga estos pasos:

    Ejecutar Endpoint de Login: Envíe un request al endpoint de login con el username y password en formato JSON.
    Obtener Token: Al autenticarse correctamente, recibirá un token que deberá usar en todos los requests subsecuentes.
    Uso del Token:
        Navegue a la sección "Headers" en Postman.
        En "Authorization", añada el token precedido por la palabra "Bearer".

Gestión de Endpoints
Ejemplos de Endpoints Comunes
Crear Encuesta:
POST /surveys
Envíe los detalles de la encuesta en el cuerpo del request.

    Publicar Encuesta:
    POST /surveys/{id}/publish

    Obtener Resultados:
    GET /surveys/{id}/results

Edición Colaborativa de Encuestas

Para manejar cambios en las encuestas de manera colaborativa, se utilizan endpoints específicos:

    Iniciar Sesión de Edición:
    POST /surveys/{id}/edit/start
    guardar cambios:
    POST /surveys/{id}/edit/save
    Enviar Cambios:
    POST /surveys/{id}/edit/submit

    Consultar Estado de Edición:
        GET /surveys/{id}/edit/status

Análisis de Datos en Tiempo Real

    Apache Kafka: Utilizado para el manejo de mensajes en tiempo real, facilitando la transmisión de respuestas de encuestas.
    Apache Spark: Permite el procesamiento y análisis en tiempo real de grandes volúmenes de datos, generando representaciones visuales mediante gráficos.
    Neo4J: Usado para analizar relaciones complejas entre respuestas de encuestados, identificando patrones y correlaciones mediante bases de datos gráficas.

Dashboards y Visualización de Datos

Para la creación de dashboards y el consumo de datos, se integran herramientas como Streamlit, permitiendo una visualización interactiva y en tiempo real de los resultados de las encuestas.
