// init-mongo.js

// Conectarse a la base de datos
var db = db.getSiblingDB("EncuestasDB");

// Crear la colección "encuestas" si no existe
db.encuestas.createIndex({ id_encuesta: 1 }, { unique: true });

// Insertar la encuesta en la colección "encuestas"
db.encuestas.insertMany([
  {
    id_encuesta: "1",
    publica: "True",
    titulo_encuesta: "Encuesta de satisfacción",
    preguntas: [
      {
        texto_pregunta: "¿Cómo calificarías nuestro servicio?",
        tipo_pregunta: "escala_calificacion",
        posibles_respuestas: [
          "Muy malo",
          "Malo",
          "Regular",
          "Bueno",
          "Muy bueno",
        ],
      },
      {
        texto_pregunta: "¿Recomendarías nuestro producto?",
        tipo_pregunta: "eleccion_unica",
        posibles_respuestas: ["Sí", "No"],
      },
    ],
  },
  {
    id_encuesta: "2",
    publica: "False",
    titulo_encuesta: "Encuesta de opinión",
    preguntas: [
      {
        texto_pregunta: "¿Cuál es tu opinión sobre nuestro nuevo servicio?",
        tipo_pregunta: "abierta",
        posibles_respuestas: null,
      },
      {
        texto_pregunta: "¿Qué tan satisfecho estás con la atención al cliente?",
        tipo_pregunta: "escala_calificacion",
        posibles_respuestas: [
          "Nada satisfecho",
          "Poco satisfecho",
          "Neutral",
          "Satisfecho",
          "Muy satisfecho",
        ],
      },
    ],
  },
]);

// Crear la colección "respuestas" si no existe
db.createCollection("respuestas");

// Crear el índice único en encuesta_id y usuario_id
db.respuestas.createIndex({ encuesta_id: 1, usuario_id: 1 }, { unique: false });

// Insertar los documentos de respuesta
db.respuestas.insertMany([{
  encuesta_id: "1",
  usuario_id: "1",
  preguntas: [
    {
    pregunta_num: "1",
    texto_pregunta: "¿Cómo calificarías nuestro servicio?",
    respuesta: "Regular",
    },{
      pregunta_num: "2",
      texto_pregunta: "¿Recomendarías nuestro producto?",
      respuesta: "Sí",
      },
    ]
  },
    {
    encuesta_id: "2",
    usuario_id: "1",
    preguntas: [
      {
      pregunta_num: "1",
      texto_pregunta: "¿Cuál es tu opinión sobre nuestro nuevo servicio?",
      respuesta: "Es muy bueno",
      },{
        pregunta_num: "2",
        texto_pregunta: "¿Qué tan satisfecho estás con la atención al cliente?",
        respuesta: "Muy satisfecho",
        },
      ],
    },
]);