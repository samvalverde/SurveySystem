CREATE DATABASE tasks;

\c tasks;

CREATE TABLE TipoRole (
  Id SERIAL PRIMARY KEY,
  Nombre VARCHAR(255) NOT NULL
);

CREATE TABLE Usuario (
  Id SERIAL PRIMARY KEY,
  Nombre VARCHAR(255) NOT NULL,
  Username VARCHAR(255) NOT NULL,
  Password VARCHAR(255) NOT NULL,
  IdTipoRole INT NOT NULL
);

CREATE TABLE EncuestaXTipoRole (
  Id SERIAL PRIMARY KEY,
  IdEncuesta INT NOT NULL,
  IdTipoRole INT NOT NULL
);

CREATE TABLE Encuesta (
  Id INT PRIMARY KEY,
  Nombre VARCHAR(255) NOT NULL
);

CREATE TABLE EncuestaXUsuario (
  Id SERIAL PRIMARY KEY,
  IdEncuesta INT NOT NULL,
  IdUsuario INT NOT NULL,
  FechaAsignacion DATE NOT NULL,
  Completada INT NOT NULL DEFAULT (0)
);

CREATE TABLE RespuestaEncuesta (
  Id SERIAL PRIMARY KEY,
  IdEncuestaXUsuario INT NOT NULL,
  FechaRespuesta DATE NOT NULL
);

ALTER TABLE Usuario 
  ADD CONSTRAINT FK_Usuario_TipoRole
  FOREIGN KEY (IdTipoRole) 
  REFERENCES TipoRole (Id);

ALTER TABLE EncuestaXTipoRole 
  ADD CONSTRAINT FK_EncuestaXTipoRole_Encuesta
  FOREIGN KEY (IdEncuesta) 
  REFERENCES Encuesta (Id);

ALTER TABLE EncuestaXTipoRole 
  ADD CONSTRAINT FK_EncuestaXTipoRole_TipoRole
  FOREIGN KEY (IdTipoRole) 
  REFERENCES TipoRole (Id);

ALTER TABLE EncuestaXUsuario
  ADD CONSTRAINT FK_EncuestaXUsuario_Encuesta
  FOREIGN KEY (IdEncuesta) 
  REFERENCES Encuesta (Id);

ALTER TABLE EncuestaXUsuario
  ADD CONSTRAINT FK_EncuestaXUsuario_Usuario
  FOREIGN KEY (IdUsuario) 
  REFERENCES Usuario (Id);

ALTER TABLE RespuestaEncuesta
  ADD CONSTRAINT FK_RespuestaEncuesta_EncuestaXUsuario
  FOREIGN KEY (IdEncuestaXUsuario) 
  REFERENCES EncuestaXUsuario (Id);