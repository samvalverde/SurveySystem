CREATE DATABASE tasks;

\c tasks;

CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  due_date DATE NOT NULL,
  status VARCHAR(10) NOT NULL,
  usuario int NOT NULL
  );

