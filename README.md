# SurveySystem

The goal of the project is to design and implement a back-end survey system using Docker, Docker Compose, MongoDB, PostgreSQL, Redis and RestAPI. This system will allow users to create, publish
and manage surveys with different types of questions, as well as register and manage lists of respondents.

En el proyecto se encuentra una carpeta llamada "python-flask-restapi", la cual contiene los archivos principales que se ejecutan para el funcionamiento del sistema. Para levantar el sistema es necesario el archivo llamado "docker-compose.yml", en este archivo se declaran los servicios que se utilizarán, así como sus respectivas características como las imágenes, puertos, volúmenes y variables de entorno. Se encuentran también definidas las bases de datos que se utilizaron, en este caso en PostgreSQL y MongoDB, con sus respectivos datos insertados.

Primeramente, es necesario aclarar que se necesita tener instalado y ejecutando Docker Desktop así como tener en el sistema dockercompose para manejo de dependencia y evitar cualquier inconveniente.

Para empezar a ejecutar el sistema se debe abrir una terminal, en la cual se deberá ubicar la dirección del python-flask-restapi. Una vez que se encuentra en esta dirección debe ejecutar el siguiente comando:

"docker-compose up --build"

Este comando levantará los servicios declarados en el docker-compose, así como los volúmenes requeridos y los comandos solicitados para conectar las bases de datos y guardar los datos que estas contienen. Una vez que se hayan ejecutado y estén corriendo todos los archivos exitosamente, se puede proceder a utilizar las funciones del sistema por medio de los endpoints que se encuentran guardados en las colecciones de Postman. En el siguiente enlace se brindará acceso a dichas colecciones en Postman:

https://app.getpostman.com/join-team?invite_code=e59ba8eaca721167264e766626873c6d&target_code=1481d8da825688d73ee1892e8fb3eb87

En este workspace se encuentran todos los endpoints solicitados para cada funcionalidad del sistema, divididos en sus respectivas secciones. Para ejecutar y probar un endpoint solo necesita seleccionar el que se desea probar y ahí se encontrarán guardadas tanto la dirección del endpoint como los datos que se deben enviar como parámetro en caso de ser necesario.

Para realizar correctamente el proceso y asegurarse de que todo funcione adecuadamente, primero se debe ejecutar el endpoint de login, en el cual se debe enviar por parámetro, en formato JSON, el username y password del usuario. En la sección a la que pertenece este endpoint se encuentran ya ciertas variables de diferentes usuarios sugeridos con los que se puede ingresar, para revisar su estructura y evitar errores de sintaxis. Al ejecutar este endpoint se retornará un código token el cual se debe copiar y utilizar en todos los endpoints para obtener acceso a la información, ya que esta se encuentra protegida y no es de acceso público.

Es importante destacar los accesos a los endpoints están ligados al tipo de usuario que ingrese, ya sea administrador, editor o encuestado, y según su rol así será su nivel de acceso a la información a través de los endpoints.

Siguiendo con el flujo del funcionamiento del sistema, una vez adquirido el token, si se quiere ejecutar otro endpoint, luego de seleccionarlo, se debe ingresar a la sección de "Headers" en la cual se encuentra una opción que dice "Authorization" la cual estará checkeada, y a la par, en la columna "Value", se encontrará la palabra "Bearer", a la par de esta palabra deberá copiar el token obtenido anteriormente, y de esta forma podrá enviar el request por medio del endpoint.

Hay ciertos endpoints en los que se ingresa información nueva o se modifica información existente, para lo cual se necesita enviar dicha información por medio de parametros en la sección de "Body->raw", en la colección de Postman estos endpoints ya tiene guardada, a modo de variable en su respectiva sección, información sugerida con la que se puede realizar el request, y así mismo se podrá consultar la estructura del JSON que se debe enviar por parámetro en cada caso.

Para consultar la información guardada en las variables se debe ingresar a una sección y revisar la pestaña de "Variables", en la cual se encontrarán todas plantillas que se utilizarán en algún endpoint correspondiente a esa sección como parámetro en caso de ser realizar un método POST o PUT, por ejemplo.
