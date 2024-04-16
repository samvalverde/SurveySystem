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

    def get_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Usuario;")
        data = cursor.fetchall()
        cursor.close()
        return data

    def create_task(self, task):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO tasks (title, description, due_date, status, usuario) VALUES ('{task['title']}', '{task['description']}','{task['due_date']}','{task['status']}','{task['usuario']}');"
        )
        self.conn.commit()
        cursor.close()
        return task

    def get_tasks_by_ID(self, request_task_id):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM tasks WHERE id = {request_task_id};")
        data = cursor.fetchall()
        cursor.close()
        return data

    def update_task(self, request_task, request_task_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE tasks SET title = '{request_task['title']}', description = '{request_task['description']}', due_date = '{request_task['due_date']}', status = '{request_task['status']}', usuario = '{request_task['usuario']}'  WHERE id = {request_task_id};"
        )
        self.conn.commit()
        cursor.close()
        return request_task

    def delete_task(self, request_task_id):
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM tasks WHERE id = {request_task_id};")
        self.conn.commit()
        cursor.close()
        return request_task_id
