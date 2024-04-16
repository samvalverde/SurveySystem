import psycopg2


class Database:
    def __init__(
        self,
        database="db_name",
        host="db_host",
        user="db_user",
        password="db_pass",
        port="db_port",
    ):
        self.conn = psycopg2.connect(
            database=database, host=host, user=user, password=password, port=port
        )

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
