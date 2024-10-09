# db.py
import pymysql

def get_db_connection():
    connection = pymysql.connect(
        host='localhost',  # e.g., 'localhost'
        user='root',
        password='root',
        database='webapp'
    )
    return connection
