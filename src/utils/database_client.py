import mysql.connector


class DatabaseClient:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
        )

    def disconnect(self):
        self.connection.close()

    def execute(self, query, params=None):
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        cursor.close()
        self.disconnect()
        return cursor.lastrowid

    def fetch(self, query, params=None):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        self.disconnect()
        return result

    def fetch_one(self, query, params=None):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        self.disconnect()
        return result

    def fetch_many(self, query, params=None):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchmany()
        cursor.close()
        self.disconnect()
        return result
