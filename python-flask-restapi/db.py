# import psycopg2


class Database:
    def __init__(self, conection):
        self.conn = conection

    def login_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM Usuario WHERE Username = '{username}' AND Password = '{password}';"
        )
        data = cursor.fetchall()
        cursor.close()
        return data

    def get_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Usuario;")
        data = cursor.fetchall()
        cursor.close()
        return data

    def create_user(self, pUser):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Usuario (Nombre, Username, Password, IdTipoRole) VALUES ('{pUser['Nombre']}', '{pUser['Username']}','{pUser['Password']}','{pUser['IdTipoRole']}');"
        )
        self.conn.commit()
        cursor.close()
        return pUser

    def get_User_by_ID(self, request_user_id):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM Usuario WHERE Id = {request_user_id};")
        data = cursor.fetchall()
        cursor.close()
        return data

    def update_user(self, request_user, request_user_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE Usuario SET Nombre = '{request_user['Nombre']}', Username = '{request_user['Username']}', Password = '{request_user['Password']}', IdTipoRole = '{request_user['IdTipoRole']}' WHERE Id = {request_user_id};"
        )
        self.conn.commit()
        cursor.close()
        return request_user

    def delete_user(self, request_user_id):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM Usuario WHERE Id = {request_user_id};")
        self.conn.commit()
        cursor.close()
        return request_user_id

    def insert_encuesta(self, pEncuesta):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Encuesta (Id, Nombre) VALUES ('{pEncuesta['id_encuesta']}', '{pEncuesta['titulo_encuesta']}');"
        )
        self.conn.commit()
        cursor.close()
        return pEncuesta

    def update_encuesta(self, encuesta_id, pEncuesta):
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE Encuesta SET Nombre = '{pEncuesta['titulo_encuesta']}' WHERE Id = {encuesta_id};"
        )
        self.conn.commit()
        cursor.close()
        return pEncuesta

    def delete_encuesta(self, encuesta_id):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM Encuesta WHERE Id = {encuesta_id};")
        self.conn.commit()
        cursor.close()
        return encuesta_id

    # Sección de encuestados
    def get_respondents(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Usuario WHERE IdTipoRole = 3;")
        data = cursor.fetchall()
        cursor.close()
        return data

    def create_respondent(self, pRespondent):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Usuario (Nombre, Username, Password, IdTipoRole) VALUES ('{pRespondent['Nombre']}', '{pRespondent['Username']}','{pRespondent['Password']}',3);"
        )
        self.conn.commit()
        cursor.close()
        return pRespondent

    def get_respondent_by_ID(self, request_respondent_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM Usuario WHERE Id = {request_respondent_id} AND IdTipoRole = 3;"
        )
        data = cursor.fetchall()
        cursor.close()
        return data

    def update_respondent(self, request_respondent, request_respondent_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE Usuario SET Nombre = '{request_respondent['Nombre']}', Username = '{request_respondent['Username']}', Password = '{request_respondent['Password']}' WHERE Id = {request_respondent_id} AND IdTipoRole = 3;"
        )
        self.conn.commit()
        cursor.close()
        return request_respondent

    def delete_respondent(self, request_respondent_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"DELETE FROM Usuario WHERE Id = {request_respondent_id} AND IdTipoRole = 3;"
        )
        self.conn.commit()
        cursor.close()
        return request_respondent_id
