\c tasks;

INSERT INTO TipoRole (Nombre) VALUES 
    ('Admin')
  , ('CreadorEncuestas')
  , ('Encuestado');

INSERT INTO Usuario (Nombre, Username, Password, IdTipoRole) VALUES 
    ('Erick', 'ekauffmann', '123', 3)
  , ('Cristopher', 'crisac', '123', 2)
  , ('Kenneth', 'kennorsdb', '123', 1);

INSERT INTO Encuesta (Id, Nombre) VALUES 
    (1, 'Encuesta de satisfacción')
  , (2, 'Encuesta de opinión');

INSERT INTO EncuestaXUsuario (IdEncuesta, IdUsuario, FechaAsignacion) VALUES 
    (1, 1, '2024-04-15')
  , (2, 1, '2024-04-15');

INSERT INTO RespuestaEncuesta (IdEncuestaXUsuario, FechaRespuesta) VALUES 
    (2, '2024-04-16');

UPDATE EncuestaXUsuario 
SET Completada = 1
WHERE IdEncuesta = 2;

